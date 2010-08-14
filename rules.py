# Rules plugin based on original rules contained in admin.py
# Updated to handle file based rule sets containing ANSI characters
# Language map will filter characters and make ready for ASCII
# Recommend ANSI Declaration for B3 to take full advantage of character set
# 2010-07-14 Rhidalin Bytes - Updated for common language files
# 2010-07-20 Added ability to send specific rule by language
# 2010-08-13 Admin notified of rules success
#            Single rules available similar to spam

__version__ = '1.2'
__author__  = 'Bakes'

import b3, re, sys, thread, string, codecs, time
import b3.events
#--------------------------------------------------------------------------------------------------
class RulesPlugin(b3.plugin.Plugin):
    _adminPlugin = None
    files = {}
	# rulestorage = {idx: 1, lang: 'cryll', number: 1, rule: 'Rule 1 - This is the rule' }
    rulestorage = {}

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
                self.files[f] = self.config.get('files', f)
            if self.files:
                idx = 1
                for n in self.files:
                    in_file = codecs.open(self.files[n], 'r', 'dbcs')
                    L = in_file.readline()
                    repr(L)
                    number = 1
                    while L:
                        self.rulestorage[idx] = n ,number , L
                        number = number + 1
                        idx = idx + 1
                        L = in_file.readline()
                        repr(L)
                    in_file.close()

        self.debug('Started')


    def getCmd(self, cmd):
        cmd = 'cmd_%s' % cmd
        if hasattr(self, cmd):
            func = getattr(self, cmd)
            return func

        return None
    def cmd_languages(self, data, client=None, cmd=None):
        """\
        - List available rule languages
        """
        lang = []
        for n in self.files:
            lang.append(n)
        cmd.sayLoudOrPM(client, string.join(lang, ', '))

    def cmd_rules(self, data, client=None, cmd=None):
        """\
        - say the rules with option language or single rule. <target> <language> <rule number> !languages for list
        """

        if not self._adminPlugin.aquireCmdLock(cmd, client, 60, True):
            client.message('^7Do not spam commands')
            return
        if client.maxLevel >= self._adminPlugin.config.getint('settings', 'admins_level'):
           pass
        else:
            client.message('^7Stop trying to spam other players')
            return
           
        if data:
            m = self._adminPlugin.parseUserCmd(data)
            if m[0] not in self.files:
                sclient = self._adminPlugin.findClientPrompt(m[0], client)
                if sclient.maxLevel >= client.maxLevel:
                    client.message('%s ^7already knows the rules' % sclient.exactName)
                    return
            else:
                thread.start_new_thread(self._sendRules, (None, lang, rule))
            if m[1]:
                try:
                    if m[1] not in self.files:
                        rule = m[1]
                        thread.start_new_thread(self._sendRules, (sclient, None, rule))
                    else:
                        lang, rule = m[1].split(' ')
                        if lang in self.file:
                            rule = int(rule)
                            thread.start_new_thread(self._sendRules, (sclient, lang, rule))
                except:
                    lang = m[1]
                    thread.start_new_thread(self._sendRules, (sclient, lang))
            else:
                thread.start_new_thread(self._sendRules, (sclient,))
        elif cmd.loud:
            thread.start_new_thread(self._sendRules, (None,))
        else:
            sclient = client
            thread.start_new_thread(self._sendRules, (sclient,))
        client.message('Yes sir, spamming the rule(s) to %s' % sclient.exactName)


    def _sendRules(self, sclient, lang=None, rule=None ):
        rus = []
        if not lang:
            if rule:
                rus.append(self._adminPlugin.config.getTextTemplate('spamages', 'rule%s' % rule))
            else:
                for i in range(1, 20):
                    try:
                        xmlrule = self._adminPlugin.config.getTextTemplate('spamages', 'rule%s' % i)
                        rus.append(xmlrule)
                    except:
                        break
        elif not rule:
            for n in self.rulestorage:
                l ,r, t = self.rulestorage[n]
                fix = t.encode('us-ascii', 'replace')
                if l == lang:
                    rus.append(fix.replace('?', ''))
        else:
            for n in self.rulestorage:
                l ,r ,t = self.rulestorage[n]
                fix = t.encode('us-ascii', 'replace')
                if l == lang and r == rule:
                    rus.append(fix.replace('?', ''))
        if sclient:
            client = sclient
            for rl in rus:
                client.message(rl)
                time.sleep(1)
        else:
            for rl in rus:
                self.console.say(rl)
                time.sleep(1)