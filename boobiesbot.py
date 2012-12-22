#!/usr/bin/python

# twisted imports
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol

# SQLite
import sqlite3

# system imports
import sys, os.path
from time import gmtime, strftime

from GenericIRCBot import GenericIRCBot, GenericIRCBotFactory, log

class BoobiesBot(GenericIRCBot):
    def __init__(self):
	self.commandData = {
	    "!help": { 
	    	"fn": self.handle_HELP, 
		"argc": 0, 
		"tillEnd": False,
		"help": "this help text",
	    },
	    "!boobies": { 
	    	"fn": self.handle_BOOBIES, 
		"argc": self.DontCheckARGC, 
		"tillEnd": True,
		"help": "get a random boobies link, or add one if argument is given",
	    },
            "!delboobies": {
                "fn": self.handle_DEL,
                "argc": 1,
                "tillEnd": True,
                "help": "delete a boobies URL by ID",
            },
	}

	self.commands = {
	    # only in direct user message, first word is the command
	    "private": ["!help", "!boobies", "!delboobies"],
	    # only in channels, first word must be the command
	    "public": ["!boobies", "!delboobies"],
	    # only in channels, first word is the name of this bot followed by a colon, second word is the command
	    "directed": ["!boobies", "!delboobies"],
	}

    def handle_BOOBIES(self, msgtype, user, recip, cmd, url=""): #{{{
        if url and url.startswith("http://"):
	    bid = self.factory.db_addBoobies(url)
	    self.sendMessage(msgtype, user, recip, "Thanks for the boobies (id=%d)! <3" % bid)
	else:
	    (url, bid) = self.factory.db_getRandomBoobies()
	    if url:
	        self.sendMessage(msgtype, user, recip, "[%d] %s" % (bid, url))
	    else:
	        self.sendMessage(msgtype, user, recip, "No boobies yet :(")
#}}}
    def handle_DEL(self, msgtype, user, recip, cmd, boobieid): #{{{
        if not boobieid.isdigit():
            self.sendMessage(msgtype, user, recip, "The del command takes 1 numeric argument")
        else:
            boobieid = int(boobieid)
	    self.factory.db_delBoobies(boobieid)
	    self.sendMessage(msgtype, user, recip, "removed boobies url %d" % boobieid)

#}}}

    def joined(self, channel):
        pass

class BoobiesBotFactory(GenericIRCBotFactory):
    def __init__(self, proto, channel, nick, fullname, url): #{{{
        GenericIRCBotFactory.__init__(self, proto, channel, nick, fullname, url)
	# if the db file doesn't exist, create it
	self.db_init("/vulnbot/boobiesbot/boobies.db")
# }}}
    def db_init(self, fn): #{{{
	if os.path.exists(fn):
	    self.db = sqlite3.connect(fn)
	else:
	    self.db = sqlite3.connect(fn)
	    cu = self.db.cursor()
	    cu.execute("create table boobies (url varchar)")
	    self.db.commit()
    #}}}
    def db_addBoobies(self, url): #{{{
	cu = self.db.cursor()
	cu.execute("insert into boobies values(?)", (url,))
	self.db.commit()
        return cu.lastrowid
    #}}}
    def db_getRandomBoobies(self): #{{{
	cu = self.db.cursor()
	cu.execute("select url, rowid from boobies order by random() limit 1")
	row = cu.fetchone()
	if row:
	    return (str(row[0]), int(row[1]))
	else:
	    return ("", 0)
    #}}}
    def db_delBoobies(self, bid): #{{{
        cu = self.db.cursor()
        cu.execute("delete from boobies where rowid=%d" % bid)
        self.db.commit()
    #}}}    


if __name__ == '__main__':
    # create factory protocol and application
    f = BoobiesBotFactory(BoobiesBot, ["#social"], "BoobiesBot", "Boobiesbot", "http://www.overthewire.org/wargames/vulnbot/")

    # connect factory to this host and port
    reactor.connectTCP("irc.overthewire.org", 6667, f)

    # run bot
    reactor.run()

