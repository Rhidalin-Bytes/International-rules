
__version__ = '1.0'
__author__  = 'Bakes'

import b3, re, threading, sys, thread, string, codecs, time
import b3.events
# Import the necessary libaries you need here, for example, I need random for the randomization of answers part of it.
import random
#--------------------------------------------------------------------------------------------------
#This lot doesn't need to be changed for simple commands, it gets the admin plugin and registers commands.
class RulesPlugin(b3.plugin.Plugin):
    _adminPlugin = None
    file = {}
    rules = {}

    def startup(self):
        """\
        Initialize plugin settings
        """

        #get the admin plugin so we can register commands
        self._adminPlugin = self.console.getPlugin('admin')
        if not self._adminPlugin:
            # something is wrong, can't start without admin plugin
            self.error('Could not find admin plugin')
            return False
        
        # register our commands (you can ignore this bit)
        if 'commands' in self.config.sections():
            for cmd in self.config.options('commands'):
                level = self.config.get('commands', cmd)
                sp = cmd.split('-')
                alias = None
                if len(sp) == 2:
                    cmd, alias = sp

            func = self.getCmd(cmd)
            if func:
                self._adminPlugin.registerCommand(self, cmd, level, func, alias)
        # find out which language files are available in config and make sure they are there.
        if 'files' in self.config.sections():
            cnt = 1
            for f in self.config.options('files'):
                self.file[f] = self.config.get('files', f)
            cnt = len(self.file)
            self.debug('cnt = %s' % cnt)
            self.debug(self.file)
            if self.file:
                cnt = 1
                for n in self.file:
                    self.debug('n = %s' % n)
                    f = codecs.open(self.file[n], 'r', 'dbcs')
                    l = f.readline()
                    repr(l)
                    while l:
                    #for line in f:
                        self.rules[cnt] = n , l
                        cnt = cnt + 1
                        l = f.readline()
                        #l.encode('us-ascii', 'replace')
                        #repr(l)
                    f.close()
            #self.debug(self.rules)
            #for n in self.rules:
            #    t, u = self.rules[n]
            #    self.debug('rules for %s , %s' % (t, u))

        self.debug('Started')


    def getCmd(self, cmd):
        cmd = 'cmd_%s' % cmd
        if hasattr(self, cmd):
            func = getattr(self, cmd)
            return func

        return None

    def cmd_rules(self, data, client=None, cmd=None):
        """\
        - say the rules to <target> with option for languages
        """
        if not self._adminPlugin.aquireCmdLock(cmd, client, 60, True):
            client.message('^7Do not spam commands')
            return
        lang = None
        m = self._adminPlugin.parseUserCmd(data)
        if m:
            try:
                if m[0] and not m[1]:
                    if client.maxLevel >= self._adminPlugin.config.getint('settings', 'admins_level'):
                        sclient = self._adminPlugin.findClientPrompt(m[0], client)
                        if not sclient:
                            return

                        if sclient.maxLevel >= client.maxLevel:
                            client.message('%s ^7already knows the rules' % sclient.exactName)
                            return
                        else:
                            client.message('^7Sir, Yes Sir!, spamming rules to %s' % sclient.exactName)
                            thread.start_new_thread(self._sendRules, (sclient,))
                    else:
                        client.message('^7Stop trying to spam other players')
                        return
                elif m[1]:
                    if client.maxLevel >= self._adminPlugin.config.getint('settings', 'admins_level'):
                        sclient = self._adminPlugin.findClientPrompt(m[0], client)
                        if not sclient:
                            return
                        if sclient.maxLevel >= client.maxLevel:
                            client.message('%s ^7already knows the rules' % sclient.exactName)
                            return
                        else:
                            client.message('^7Sir, Yes Sir!, spamming rules to %s' % sclient.exactName)
                            thread.start_new_thread(self._sendRules, (sclient, m[1]))
                    else:
                        client.message('^7Stop trying to spam other players')
                        return
            except:
                pass
        elif cmd.loud:
            thread.start_new_thread(self._sendRules, (None,))
            return
        else:
            sclient = client
            thread.start_new_thread(self._sendRules, (sclient,))

    def _sendRules(self, sclient, lang='cryll'):
        rus = []
        if not lang:
            #for i in range(1, 20):
            #    try:
            #        rule = self.config.getTextTemplate('spamages', 'rule%s' % i)
            #        rus.append(rule)
            #    except:
            #        break
            for n in self.rules:
                l , t = self.rules[n]
                if l == lang:
                    rus.append(t)

        else:
            for n in self.rules:
                l , t = self.rules[n]
                a = t.encode('us-ascii', 'replace')
                a.replace('?', '')
                if l == lang:
                    rus.append(a)
            #add lines as rule in rules
            #close text file
        if sclient:
            for rule in rus:
                sclient.message(rule)
                time.sleep(1)
        else:
            for rule in rus:
                self.console.say(rule)
                time.sleep(1)