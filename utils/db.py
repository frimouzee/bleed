import aiosqlite
import os
import json
import time

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bot.db")

async def initxoxoxoxdb():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS prefixes (
                guildxoxoxoxid INTEGER PRIMARY KEY,
                prefix TEXT NOT NULL
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS antinukexoxoxoxsettings (
                guildxoxoxoxid INTEGER PRIMARY KEY,
                enabled INTEGER DEFAULT 0,
                punishment TEXT DEFAULT 'strip'
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS antinuke_modules (
                guildxoxoxoxid INTEGER,
                module_name TEXT,
                enabled INTEGER DEFAULT 0,
                threshold INTEGER DEFAULT 3,
                punishment TEXT,
                PRIMARY KEY (guildxoxoxoxid, module_name)
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS antinuke_whitelist (
                guildxoxoxoxid INTEGER,
                userxoxoxoxid INTEGER,
                PRIMARY KEY (guildxoxoxoxid, userxoxoxoxid)
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS antinuke_trust (
                guildxoxoxoxid INTEGER,
                userxoxoxoxid INTEGER,
                PRIMARY KEY (guildxoxoxoxid, userxoxoxoxid)
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS automod_settings (
                guildxoxoxoxid INTEGER PRIMARY KEY,
                enabled INTEGER DEFAULT 0,
                punishment TEXT DEFAULT 'timeout',
                timeout_duration INTEGER DEFAULT 60
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS automod_filters (
                guildxoxoxoxid INTEGER,
                word TEXT,
                PRIMARY KEY (guildxoxoxoxid, word)
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS automod_rules (
                guildxoxoxoxid INTEGER,
                rule_name TEXT,
                enabled INTEGER DEFAULT 0,
                threshold INTEGER DEFAULT 5,
                PRIMARY KEY (guildxoxoxoxid, rule_name)
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS automod_whitelist (
                guildxoxoxoxid INTEGER,
                target_id INTEGER,
                target_type TEXT, -- 'user', 'role', 'channel'
                events TEXT, -- comma-separated rule list or 'all'
                reason TEXT,
                PRIMARY KEY (guildxoxoxoxid, target_id)
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS giveaways (
                messagexoxoxoxid INTEGER PRIMARY KEY,
                channelxoxoxoxid INTEGER,
                guildxoxoxoxid INTEGER,
                prize TEXT,
                winnersxoxoxoxcount INTEGER,
                hostxoxoxoxid INTEGER,
                endxoxoxoxtime REAL,
                active INTEGER DEFAULT 1
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS giveaway_blacklists (
                guildxoxoxoxid INTEGER,
                rolexoxoxoxid INTEGER,
                PRIMARY KEY (guildxoxoxoxid, rolexoxoxoxid)
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS giveaway_limits (
                guildxoxoxoxid INTEGER,
                rolexoxoxoxid INTEGER,
                maxxoxoxoxentries INTEGER,
                PRIMARY KEY (guildxoxoxoxid, rolexoxoxoxid)
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS afk (
                userxoxoxoxid INTEGER PRIMARY KEY,
                status TEXT,
                timestamp REAL
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS snipes (
                channelxoxoxoxid INTEGER,
                author_id INTEGER,
                content TEXT,
                timestamp REAL,
                attachments TEXT
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS editsnipes (
                channelxoxoxoxid INTEGER,
                author_id INTEGER,
                oldxoxoxoxcontent TEXT,
                timestamp REAL
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS reactionsnipes (
                channelxoxoxoxid INTEGER,
                userxoxoxoxid INTEGER,
                messagexoxoxoxid INTEGER,
                emoji TEXT,
                timestamp REAL
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS confessions_config (
                guildxoxoxoxid INTEGER PRIMARY KEY,
                channelxoxoxoxid INTEGER
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS sticky_messages (
                channelxoxoxoxid INTEGER PRIMARY KEY,
                message TEXT NOT NULL
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS voicemaster_config (
                guildxoxoxoxid INTEGER PRIMARY KEY,
                categoryxoxoxoxid INTEGER,
                channelxoxoxoxid INTEGER,
                template TEXT DEFAULT "{owner}'s channel",
                deletexoxoxoxempty INTEGER DEFAULT 1
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS voicemaster_channels (
                channelxoxoxoxid INTEGER PRIMARY KEY,
                owner_id INTEGER,
                guildxoxoxoxid INTEGER
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS tickets_config (
                guildxoxoxoxid INTEGER PRIMARY KEY,
                panelxoxoxoxchannelxoxoxoxid INTEGER,
                openxoxoxoxcategoryxoxoxoxid INTEGER,
                supportxoxoxoxrolexoxoxoxid INTEGER,
                openxoxoxoxemoji TEXT DEFAULT '🎫',
                deletexoxoxoxemoji TEXT DEFAULT '🗑️',
                panelxoxoxoxmessagexoxoxoxid INTEGER
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                channelxoxoxoxid INTEGER PRIMARY KEY,
                guildxoxoxoxid INTEGER,
                owner_id INTEGER,
                closed INTEGER DEFAULT 0
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS levels_config (
                guildxoxoxoxid INTEGER PRIMARY KEY,
                enabled INTEGER DEFAULT 0,
                messagexoxoxoxchannelxoxoxoxid INTEGER,
                messagexoxoxoxtemplate TEXT DEFAULT "GG {user.mention}, you leveled up to level **{level}**!"
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS levels (
                guildxoxoxoxid INTEGER,
                userxoxoxoxid INTEGER,
                xp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 0,
                PRIMARY KEY (guildxoxoxoxid, userxoxoxoxid)
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS welcome_config (
                guildxoxoxoxid INTEGER PRIMARY KEY,
                channelxoxoxoxid INTEGER,
                message TEXT,
                autoxoxoxoxdelete INTEGER DEFAULT 0
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS leave_config (
                guildxoxoxoxid INTEGER PRIMARY KEY,
                channelxoxoxoxid INTEGER,
                message TEXT,
                autoxoxoxoxdelete INTEGER DEFAULT 0
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS logging_config (
                guildxoxoxoxid INTEGER PRIMARY KEY,
                channelxoxoxoxid INTEGER,
                events TEXT DEFAULT 'all'
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS ping_on_join (
                guildxoxoxoxid INTEGER PRIMARY KEY,
                channelxoxoxoxid INTEGER,
                threshold INTEGER DEFAULT 5
            )
        """)

        await db.commit()

async def getxoxoxoxprefix(guildxoxoxoxid: int) -> str:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT prefix FROM prefixes WHERE guildxoxoxoxid = ?", (guildxoxoxoxid,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else ","

async def set_prefix(guildxoxoxoxid: int, prefix: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO prefixes (guildxoxoxoxid, prefix) VALUES (?, ?)
            ON CONFLICT(guildxoxoxoxid) DO UPDATE SET prefix = excluded.prefix
        """, (guildxoxoxoxid, prefix))
        await db.commit()

async def getxoxoxoxwelcomexoxoxoxconfig(guildxoxoxoxid: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT channelxoxoxoxid, message, autoxoxoxoxdelete FROM welcome_config WHERE guildxoxoxoxid = ?", (guildxoxoxoxid,)) as cursor:
            return await cursor.fetchone()

async def setxoxoxoxwelcomexoxoxoxconfig(guildxoxoxoxid: int, channelxoxoxoxid: int, message: str = None, autoxoxoxoxdelete: int = 0):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO welcome_config (guildxoxoxoxid, channelxoxoxoxid, message, autoxoxoxoxdelete)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(guildxoxoxoxid) DO UPDATE SET 
                channelxoxoxoxid = COALESCE(excluded.channelxoxoxoxid, channelxoxoxoxid),
                message = COALESCE(excluded.message, message),
                autoxoxoxoxdelete = COALESCE(excluded.autoxoxoxoxdelete, autoxoxoxoxdelete)
        """, (guildxoxoxoxid, channelxoxoxoxid, message, autoxoxoxoxdelete))
        await db.commit()

async def getxoxoxoxleavexoxoxoxconfig(guildxoxoxoxid: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT channelxoxoxoxid, message, autoxoxoxoxdelete FROM leave_config WHERE guildxoxoxoxid = ?", (guildxoxoxoxid,)) as cursor:
            return await cursor.fetchone()

async def setxoxoxoxleavexoxoxoxconfig(guildxoxoxoxid: int, channelxoxoxoxid: int, message: str = None, autoxoxoxoxdelete: int = 0):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO leave_config (guildxoxoxoxid, channelxoxoxoxid, message, autoxoxoxoxdelete)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(guildxoxoxoxid) DO UPDATE SET 
                channelxoxoxoxid = COALESCE(excluded.channelxoxoxoxid, channelxoxoxoxid),
                message = COALESCE(excluded.message, message),
                autoxoxoxoxdelete = COALESCE(excluded.autoxoxoxoxdelete, autoxoxoxoxdelete)
        """, (guildxoxoxoxid, channelxoxoxoxid, message, autoxoxoxoxdelete))
        await db.commit()

async def getxoxoxoxpingxoxoxoxonxoxoxoxjoin(guildxoxoxoxid: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT channelxoxoxoxid, threshold FROM ping_on_join WHERE guildxoxoxoxid = ?", (guildxoxoxoxid,)) as cursor:
            return await cursor.fetchone()

async def setxoxoxoxpingxoxoxoxonxoxoxoxjoin(guildxoxoxoxid: int, channelxoxoxoxid: int, threshold: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO ping_on_join (guildxoxoxoxid, channelxoxoxoxid, threshold)
            VALUES (?, ?, ?)
            ON CONFLICT(guildxoxoxoxid) DO UPDATE SET channelxoxoxoxid = excluded.channelxoxoxoxid, threshold = excluded.threshold
        """, (guildxoxoxoxid, channelxoxoxoxid, threshold))
        await db.commit()

async def getxoxoxoxloggingxoxoxoxconfig(guildxoxoxoxid: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT channelxoxoxoxid, events FROM logging_config WHERE guildxoxoxoxid = ?", (guildxoxoxoxid,)) as cursor:
            return await cursor.fetchone()

async def setxoxoxoxloggingxoxoxoxconfig(guildxoxoxoxid: int, channelxoxoxoxid: int, events: str = 'all'):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO logging_config (guildxoxoxoxid, channelxoxoxoxid, events)
            VALUES (?, ?, ?)
            ON CONFLICT(guildxoxoxoxid) DO UPDATE SET channelxoxoxoxid = excluded.channelxoxoxoxid, events = excluded.events
        """, (guildxoxoxoxid, channelxoxoxoxid, events))
        await db.commit()

async def getxoxoxoxafk(userxoxoxoxid: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT status, timestamp FROM afk WHERE userxoxoxoxid = ?", (userxoxoxoxid,)) as cursor:
            return await cursor.fetchone()

async def setxoxoxoxafk(userxoxoxoxid: int, status: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO afk (userxoxoxoxid, status, timestamp) VALUES (?, ?, ?)
            ON CONFLICT(userxoxoxoxid) DO UPDATE SET status = excluded.status, timestamp = excluded.timestamp
        """, (userxoxoxoxid, status, time.time()))
        await db.commit()

async def removexoxoxoxafk(userxoxoxoxid: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM afk WHERE userxoxoxoxid = ?", (userxoxoxoxid,))
        await db.commit()

async def addxoxoxoxsnipe(channelxoxoxoxid: int, author_id: int, content: str, attachments: list):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO snipes (channelxoxoxoxid, author_id, content, timestamp, attachments)
            VALUES (?, ?, ?, ?, ?)
        """, (channelxoxoxoxid, author_id, content, time.time(), json.dumps(attachments)))
        await db.execute("""
            DELETE FROM snipes WHERE channelxoxoxoxid = ? AND timestamp NOT IN (
                SELECT timestamp FROM snipes WHERE channelxoxoxoxid = ? ORDER BY timestamp DESC LIMIT 50
            )
        """, (channelxoxoxoxid, channelxoxoxoxid))
        await db.commit()

async def getxoxoxoxsnipes(channelxoxoxoxid: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT author_id, content, timestamp, attachments FROM snipes WHERE channelxoxoxoxid = ? ORDER BY timestamp DESC", (channelxoxoxoxid,)) as cursor:
            return await cursor.fetchall()

async def addxoxoxoxeditsnipe(channelxoxoxoxid: int, author_id: int, oldxoxoxoxcontent: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO editsnipes (channelxoxoxoxid, author_id, oldxoxoxoxcontent, timestamp)
            VALUES (?, ?, ?, ?)
        """, (channelxoxoxoxid, author_id, oldxoxoxoxcontent, time.time()))
        await db.execute("""
            DELETE FROM editsnipes WHERE channelxoxoxoxid = ? AND timestamp NOT IN (
                SELECT timestamp FROM editsnipes WHERE channelxoxoxoxid = ? ORDER BY timestamp DESC LIMIT 50
            )
        """, (channelxoxoxoxid, channelxoxoxoxid))
        await db.commit()

async def getxoxoxoxeditsnipes(channelxoxoxoxid: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT author_id, oldxoxoxoxcontent, timestamp FROM editsnipes WHERE channelxoxoxoxid = ? ORDER BY timestamp DESC", (channelxoxoxoxid,)) as cursor:
            return await cursor.fetchall()

async def addxoxoxoxreactionsnipe(channelxoxoxoxid: int, userxoxoxoxid: int, messagexoxoxoxid: int, emoji: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO reactionsnipes (channelxoxoxoxid, userxoxoxoxid, messagexoxoxoxid, emoji, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (channelxoxoxoxid, userxoxoxoxid, messagexoxoxoxid, emoji, time.time()))
        await db.execute("""
            DELETE FROM reactionsnipes WHERE channelxoxoxoxid = ? AND timestamp NOT IN (
                SELECT timestamp FROM reactionsnipes WHERE channelxoxoxoxid = ? ORDER BY timestamp DESC LIMIT 50
            )
        """, (channelxoxoxoxid, channelxoxoxoxid))
        await db.commit()

async def getxoxoxoxreactionsnipes(channelxoxoxoxid: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT userxoxoxoxid, messagexoxoxoxid, emoji, timestamp FROM reactionsnipes WHERE channelxoxoxoxid = ? ORDER BY timestamp DESC", (channelxoxoxoxid,)) as cursor:
            return await cursor.fetchall()

async def clearxoxoxoxsnipes(channelxoxoxoxid: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM snipes WHERE channelxoxoxoxid = ?", (channelxoxoxoxid,))
        await db.execute("DELETE FROM editsnipes WHERE channelxoxoxoxid = ?", (channelxoxoxoxid,))
        await db.execute("DELETE FROM reactionsnipes WHERE channelxoxoxoxid = ?", (channelxoxoxoxid,))
        await db.commit()

async def getxoxoxoxstickyxoxoxoxmessage(channelxoxoxoxid: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT message FROM sticky_messages WHERE channelxoxoxoxid = ?", (channelxoxoxoxid,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None

async def setxoxoxoxstickyxoxoxoxmessage(channelxoxoxoxid: int, message: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO sticky_messages (channelxoxoxoxid, message) VALUES (?, ?)
            ON CONFLICT(channelxoxoxoxid) DO UPDATE SET message = excluded.message
        """, (channelxoxoxoxid, message))
        await db.commit()

async def removexoxoxoxstickyxoxoxoxmessage(channelxoxoxoxid: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM sticky_messages WHERE channelxoxoxoxid = ?", (channelxoxoxoxid,))
        await db.commit()

async def listxoxoxoxstickyxoxoxoxmessages():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT channelxoxoxoxid, message FROM sticky_messages") as cursor:
            return await cursor.fetchall()

async def getxoxoxoxvoicemasterxoxoxoxconfig(guildxoxoxoxid: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT categoryxoxoxoxid, channelxoxoxoxid, template, deletexoxoxoxempty FROM voicemaster_config WHERE guildxoxoxoxid = ?", (guildxoxoxoxid,)) as cursor:
            return await cursor.fetchone()

async def setxoxoxoxvoicemasterxoxoxoxconfig(guildxoxoxoxid: int, categoryxoxoxoxid: int, channelxoxoxoxid: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO voicemaster_config (guildxoxoxoxid, categoryxoxoxoxid, channelxoxoxoxid) VALUES (?, ?, ?)
            ON CONFLICT(guildxoxoxoxid) DO UPDATE SET categoryxoxoxoxid = excluded.categoryxoxoxoxid, channelxoxoxoxid = excluded.channelxoxoxoxid
        """, (guildxoxoxoxid, categoryxoxoxoxid, channelxoxoxoxid))
        await db.commit()

async def setxoxoxoxvoicemasterxoxoxoxtemplate(guildxoxoxoxid: int, template: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE voicemaster_config SET template = ? WHERE guildxoxoxoxid = ?", (template, guildxoxoxoxid))
        await db.commit()

async def setxoxoxoxvoicemasterxoxoxoxtemporary(guildxoxoxoxid: int, deletexoxoxoxempty: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE voicemaster_config SET deletexoxoxoxempty = ? WHERE guildxoxoxoxid = ?", (deletexoxoxoxempty, guildxoxoxoxid))
        await db.commit()

async def addxoxoxoxvoicemasterxoxoxoxchannel(channelxoxoxoxid: int, owner_id: int, guildxoxoxoxid: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT INTO voicemaster_channels (channelxoxoxoxid, owner_id, guildxoxoxoxid) VALUES (?, ?, ?)", (channelxoxoxoxid, owner_id, guildxoxoxoxid))
        await db.commit()

async def getxoxoxoxvoicemasterxoxoxoxchannel(channelxoxoxoxid: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT owner_id, guildxoxoxoxid FROM voicemaster_channels WHERE channelxoxoxoxid = ?", (channelxoxoxoxid,)) as cursor:
            return await cursor.fetchone()

async def removexoxoxoxvoicemasterxoxoxoxchannel(channelxoxoxoxid: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM voicemaster_channels WHERE channelxoxoxoxid = ?", (channelxoxoxoxid,))
        await db.commit()

async def getxoxoxoxticketsxoxoxoxconfig(guildxoxoxoxid: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT panelxoxoxoxchannelxoxoxoxid, openxoxoxoxcategoryxoxoxoxid, supportxoxoxoxrolexoxoxoxid, openxoxoxoxemoji, deletexoxoxoxemoji, panelxoxoxoxmessagexoxoxoxid
            FROM tickets_config WHERE guildxoxoxoxid = ?
        """, (guildxoxoxoxid,)) as cursor:
            return await cursor.fetchone()

async def setxoxoxoxticketsxoxoxoxconfig(guildxoxoxoxid: int, panelxoxoxoxchannelxoxoxoxid: int, openxoxoxoxcategoryxoxoxoxid: int, supportxoxoxoxrolexoxoxoxid: int = None, openxoxoxoxemoji: str = '🎫', deletexoxoxoxemoji: str = '🗑️', panelxoxoxoxmessagexoxoxoxid: int = None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO tickets_config (guildxoxoxoxid, panelxoxoxoxchannelxoxoxoxid, openxoxoxoxcategoryxoxoxoxid, supportxoxoxoxrolexoxoxoxid, openxoxoxoxemoji, deletexoxoxoxemoji, panelxoxoxoxmessagexoxoxoxid)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(guildxoxoxoxid) DO UPDATE SET
                panelxoxoxoxchannelxoxoxoxid = COALESCE(excluded.panelxoxoxoxchannelxoxoxoxid, panelxoxoxoxchannelxoxoxoxid),
                openxoxoxoxcategoryxoxoxoxid = COALESCE(excluded.openxoxoxoxcategoryxoxoxoxid, openxoxoxoxcategoryxoxoxoxid),
                supportxoxoxoxrolexoxoxoxid = COALESCE(excluded.supportxoxoxoxrolexoxoxoxid, supportxoxoxoxrolexoxoxoxid),
                openxoxoxoxemoji = COALESCE(excluded.openxoxoxoxemoji, openxoxoxoxemoji),
                deletexoxoxoxemoji = COALESCE(excluded.deletexoxoxoxemoji, deletexoxoxoxemoji),
                panelxoxoxoxmessagexoxoxoxid = COALESCE(excluded.panelxoxoxoxmessagexoxoxoxid, panelxoxoxoxmessagexoxoxoxid)
        """, (guildxoxoxoxid, panelxoxoxoxchannelxoxoxoxid, openxoxoxoxcategoryxoxoxoxid, supportxoxoxoxrolexoxoxoxid, openxoxoxoxemoji, deletexoxoxoxemoji, panelxoxoxoxmessagexoxoxoxid))
        await db.commit()

async def addxoxoxoxticket(channelxoxoxoxid: int, guildxoxoxoxid: int, owner_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT INTO tickets (channelxoxoxoxid, guildxoxoxoxid, owner_id) VALUES (?, ?, ?)", (channelxoxoxoxid, guildxoxoxoxid, owner_id))
        await db.commit()

async def getxoxoxoxticket(channelxoxoxoxid: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT guildxoxoxoxid, owner_id, closed FROM tickets WHERE channelxoxoxoxid = ?", (channelxoxoxoxid,)) as cursor:
            return await cursor.fetchone()

async def closexoxoxoxticket(channelxoxoxoxid: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE tickets SET closed = 1 WHERE channelxoxoxoxid = ?", (channelxoxoxoxid,))
        await db.commit()

async def getxoxoxoxlevelsxoxoxoxconfig(guildxoxoxoxid: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT enabled, messagexoxoxoxchannelxoxoxoxid, messagexoxoxoxtemplate FROM levels_config WHERE guildxoxoxoxid = ?", (guildxoxoxoxid,)) as cursor:
            return await cursor.fetchone()

async def setxoxoxoxlevelsxoxoxoxconfig(guildxoxoxoxid: int, enabled: int = None, messagexoxoxoxchannelxoxoxoxid: int = None, messagexoxoxoxtemplate: str = None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO levels_config (guildxoxoxoxid, enabled, messagexoxoxoxchannelxoxoxoxid, messagexoxoxoxtemplate)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(guildxoxoxoxid) DO UPDATE SET
                enabled = COALESCE(excluded.enabled, enabled),
                messagexoxoxoxchannelxoxoxoxid = COALESCE(excluded.messagexoxoxoxchannelxoxoxoxid, messagexoxoxoxchannelxoxoxoxid),
                messagexoxoxoxtemplate = COALESCE(excluded.messagexoxoxoxtemplate, messagexoxoxoxtemplate)
        """, (guildxoxoxoxid, enabled if enabled is not None else 0, messagexoxoxoxchannelxoxoxoxid, messagexoxoxoxtemplate))
        await db.commit()

async def getxoxoxoxuserxoxoxoxlevel(guildxoxoxoxid: int, userxoxoxoxid: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT xp, level FROM levels WHERE guildxoxoxoxid = ? AND userxoxoxoxid = ?", (guildxoxoxoxid, userxoxoxoxid)) as cursor:
            return await cursor.fetchone()

async def updatexoxoxoxuserxoxoxoxlevel(guildxoxoxoxid: int, userxoxoxoxid: int, xp: int, level: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO levels (guildxoxoxoxid, userxoxoxoxid, xp, level) VALUES (?, ?, ?, ?)
            ON CONFLICT(guildxoxoxoxid, userxoxoxoxid) DO UPDATE SET xp = excluded.xp, level = excluded.level
        """, (guildxoxoxoxid, userxoxoxoxid, xp, level))
        await db.commit()

async def getxoxoxoxleaderboard(guildxoxoxoxid: int, limit: int = 10):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT userxoxoxoxid, xp, level FROM levels WHERE guildxoxoxoxid = ? ORDER BY xp DESC LIMIT ?", (guildxoxoxoxid, limit)) as cursor:
            return await cursor.fetchall()

async def getxoxoxoxantinukexoxoxoxsettings(guildxoxoxoxid: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT enabled, punishment FROM antinukexoxoxoxsettings WHERE guildxoxoxoxid = ?", (guildxoxoxoxid,)) as cursor:
            return await cursor.fetchone()

async def setxoxoxoxantinukexoxoxoxsettings(guildxoxoxoxid: int, enabled: int = None, punishment: str = None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO antinukexoxoxoxsettings (guildxoxoxoxid, enabled, punishment) VALUES (?, ?, ?)
            ON CONFLICT(guildxoxoxoxid) DO UPDATE SET
                enabled = COALESCE(excluded.enabled, enabled),
                punishment = COALESCE(excluded.punishment, punishment)
        """, (guildxoxoxoxid, enabled if enabled is not None else 0, punishment or 'strip'))
        await db.commit()

async def getxoxoxoxantinukexoxoxoxmodule(guildxoxoxoxid: int, module_name: str):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT enabled, threshold, punishment FROM antinuke_modules WHERE guildxoxoxoxid = ? AND module_name = ?", (guildxoxoxoxid, module_name)) as cursor:
            return await cursor.fetchone()

async def setxoxoxoxantinukexoxoxoxmodule(guildxoxoxoxid: int, module_name: str, enabled: int, threshold: int = 3, punishment: str = None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO antinuke_modules (guildxoxoxoxid, module_name, enabled, threshold, punishment) VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(guildxoxoxoxid, module_name) DO UPDATE SET
                enabled = excluded.enabled,
                threshold = excluded.threshold,
                punishment = COALESCE(excluded.punishment, punishment)
        """, (guildxoxoxoxid, module_name, enabled, threshold, punishment))
        await db.commit()

async def listxoxoxoxantinukexoxoxoxmodules(guildxoxoxoxid: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT module_name, enabled, threshold, punishment FROM antinuke_modules WHERE guildxoxoxoxid = ?", (guildxoxoxoxid,)) as cursor:
            return await cursor.fetchall()

async def isxoxoxoxwhitelisted(guildxoxoxoxid: int, userxoxoxoxid: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT 1 FROM antinuke_whitelist WHERE guildxoxoxoxid = ? AND userxoxoxoxid = ?", (guildxoxoxoxid, userxoxoxoxid)) as cursor:
            row = await cursor.fetchone()
            return row is not None

async def addxoxoxoxwhitelist(guildxoxoxoxid: int, userxoxoxoxid: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR IGNORE INTO antinuke_whitelist (guildxoxoxoxid, userxoxoxoxid) VALUES (?, ?)", (guildxoxoxoxid, userxoxoxoxid))
        await db.commit()

async def removexoxoxoxwhitelist(guildxoxoxoxid: int, userxoxoxoxid: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM antinuke_whitelist WHERE guildxoxoxoxid = ? AND userxoxoxoxid = ?", (guildxoxoxoxid, userxoxoxoxid))
        await db.commit()

async def listxoxoxoxwhitelist(guildxoxoxoxid: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT userxoxoxoxid FROM antinuke_whitelist WHERE guildxoxoxoxid = ?", (guildxoxoxoxid,)) as cursor:
            rows = await cursor.fetchall()
            return [r[0] for r in rows]

async def isxoxoxoxtrusted(guildxoxoxoxid: int, userxoxoxoxid: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT 1 FROM antinuke_trust WHERE guildxoxoxoxid = ? AND userxoxoxoxid = ?", (guildxoxoxoxid, userxoxoxoxid)) as cursor:
            row = await cursor.fetchone()
            return row is not None

async def addxoxoxoxtrust(guildxoxoxoxid: int, userxoxoxoxid: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR IGNORE INTO antinuke_trust (guildxoxoxoxid, userxoxoxoxid) VALUES (?, ?)", (guildxoxoxoxid, userxoxoxoxid))
        await db.commit()

async def removexoxoxoxtrust(guildxoxoxoxid: int, userxoxoxoxid: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM antinuke_trust WHERE guildxoxoxoxid = ? AND userxoxoxoxid = ?", (guildxoxoxoxid, userxoxoxoxid))
        await db.commit()

async def listxoxoxoxtrust(guildxoxoxoxid: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT userxoxoxoxid FROM antinuke_trust WHERE guildxoxoxoxid = ?", (guildxoxoxoxid,)) as cursor:
            rows = await cursor.fetchall()
            return [r[0] for r in rows]

async def getxoxoxoxconfessionsxoxoxoxconfig(guildxoxoxoxid: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT channelxoxoxoxid FROM confessions_config WHERE guildxoxoxoxid = ?", (guildxoxoxoxid,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None

async def setxoxoxoxconfessionsxoxoxoxconfig(guildxoxoxoxid: int, channelxoxoxoxid: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO confessions_config (guildxoxoxoxid, channelxoxoxoxid) VALUES (?, ?)
            ON CONFLICT(guildxoxoxoxid) DO UPDATE SET channelxoxoxoxid = excluded.channelxoxoxoxid
        """, (guildxoxoxoxid, channelxoxoxoxid))
        await db.commit()

async def removexoxoxoxconfessionsxoxoxoxconfig(guildxoxoxoxid: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM confessions_config WHERE guildxoxoxoxid = ?", (guildxoxoxoxid,))
        await db.commit()

async def getxoxoxoxautomodxoxoxoxsettings(guildxoxoxoxid: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT enabled, punishment, timeout_duration FROM automod_settings WHERE guildxoxoxoxid = ?", (guildxoxoxoxid,)) as cursor:
            return await cursor.fetchone()

async def setxoxoxoxautomodxoxoxoxsettings(guildxoxoxoxid: int, enabled: int = None, punishment: str = None, timeout_duration: int = None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO automod_settings (guildxoxoxoxid, enabled, punishment, timeout_duration)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(guildxoxoxoxid) DO UPDATE SET
                enabled = COALESCE(excluded.enabled, enabled),
                punishment = COALESCE(excluded.punishment, punishment),
                timeout_duration = COALESCE(excluded.timeout_duration, timeout_duration)
        """, (guildxoxoxoxid, enabled if enabled is not None else 0, punishment or 'timeout', timeout_duration or 60))
        await db.commit()

async def addxoxoxoxfilterxoxoxoxword(guildxoxoxoxid: int, word: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR IGNORE INTO automod_filters (guildxoxoxoxid, word) VALUES (?, ?)", (guildxoxoxoxid, word.lower()))
        await db.commit()

async def removexoxoxoxfilterxoxoxoxword(guildxoxoxoxid: int, word: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM automod_filters WHERE guildxoxoxoxid = ? AND word = ?", (guildxoxoxoxid, word.lower()))
        await db.commit()

async def listxoxoxoxfilterxoxoxoxwords(guildxoxoxoxid: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT word FROM automod_filters WHERE guildxoxoxoxid = ?", (guildxoxoxoxid,)) as cursor:
            rows = await cursor.fetchall()
            return [r[0] for r in rows]

async def clearxoxoxoxfilterxoxoxoxwords(guildxoxoxoxid: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM automod_filters WHERE guildxoxoxoxid = ?", (guildxoxoxoxid,))
        await db.commit()

async def getxoxoxoxautomodxoxoxoxrule(guildxoxoxoxid: int, rule_name: str):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT enabled, threshold FROM automod_rules WHERE guildxoxoxoxid = ? AND rule_name = ?", (guildxoxoxoxid, rule_name)) as cursor:
            return await cursor.fetchone()

async def setxoxoxoxautomodxoxoxoxrule(guildxoxoxoxid: int, rule_name: str, enabled: int, threshold: int = 5):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO automod_rules (guildxoxoxoxid, rule_name, enabled, threshold) VALUES (?, ?, ?, ?)
            ON CONFLICT(guildxoxoxoxid, rule_name) DO UPDATE SET
                enabled = excluded.enabled,
                threshold = excluded.threshold
        """, (guildxoxoxoxid, rule_name, enabled, threshold))
        await db.commit()

async def addxoxoxoxautomodxoxoxoxwhitelist(guildxoxoxoxid: int, target_id: int, target_type: str, events: str, reason: str = ""):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO automod_whitelist (guildxoxoxoxid, target_id, target_type, events, reason)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(guildxoxoxoxid, target_id) DO UPDATE SET
                target_type = excluded.target_type,
                events = excluded.events,
                reason = excluded.reason
        """, (guildxoxoxoxid, target_id, target_type, events, reason))
        await db.commit()

async def removexoxoxoxautomodxoxoxoxwhitelist(guildxoxoxoxid: int, target_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM automod_whitelist WHERE guildxoxoxoxid = ? AND target_id = ?", (guildxoxoxoxid, target_id))
        await db.commit()

async def listxoxoxoxautomodxoxoxoxwhitelist(guildxoxoxoxid: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT target_id, target_type, events, reason FROM automod_whitelist WHERE guildxoxoxoxid = ?", (guildxoxoxoxid,)) as cursor:
            return await cursor.fetchall()

async def addxoxoxoxgiveaway(messagexoxoxoxid: int, channelxoxoxoxid: int, guildxoxoxoxid: int, prize: str, winnersxoxoxoxcount: int, hostxoxoxoxid: int, endxoxoxoxtime: float):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO giveaways (messagexoxoxoxid, channelxoxoxoxid, guildxoxoxoxid, prize, winnersxoxoxoxcount, hostxoxoxoxid, endxoxoxoxtime, active)
            VALUES (?, ?, ?, ?, ?, ?, ?, 1)
        """, (messagexoxoxoxid, channelxoxoxoxid, guildxoxoxoxid, prize, winnersxoxoxoxcount, hostxoxoxoxid, endxoxoxoxtime))
        await db.commit()

async def getxoxoxoxactivexoxoxoxgiveaways():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT messagexoxoxoxid, channelxoxoxoxid, guildxoxoxoxid, prize, winnersxoxoxoxcount, hostxoxoxoxid, endxoxoxoxtime FROM giveaways WHERE active = 1") as cursor:
            return await cursor.fetchall()

async def setxoxoxoxgiveawayxoxoxoxinactive(messagexoxoxoxid: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE giveaways SET active = 0 WHERE messagexoxoxoxid = ?", (messagexoxoxoxid,))
        await db.commit()

async def getxoxoxoxgiveaway(messagexoxoxoxid: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT channelxoxoxoxid, guildxoxoxoxid, prize, winnersxoxoxoxcount, hostxoxoxoxid, endxoxoxoxtime, active FROM giveaways WHERE messagexoxoxoxid = ?", (messagexoxoxoxid,)) as cursor:
            return await cursor.fetchone()

async def addxoxoxoxgiveawayxoxoxoxblacklist(guildxoxoxoxid: int, rolexoxoxoxid: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR IGNORE INTO giveaway_blacklists (guildxoxoxoxid, rolexoxoxoxid) VALUES (?, ?)", (guildxoxoxoxid, rolexoxoxoxid))
        await db.commit()

async def removexoxoxoxgiveawayxoxoxoxblacklist(guildxoxoxoxid: int, rolexoxoxoxid: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM giveaway_blacklists WHERE guildxoxoxoxid = ? AND rolexoxoxoxid = ?", (guildxoxoxoxid, rolexoxoxoxid))
        await db.commit()

async def getxoxoxoxgiveawayxoxoxoxblacklists(guildxoxoxoxid: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT rolexoxoxoxid FROM giveaway_blacklists WHERE guildxoxoxoxid = ?", (guildxoxoxoxid,)) as cursor:
            rows = await cursor.fetchall()
            return [r[0] for r in rows]

async def setxoxoxoxgiveawayxoxoxoxlimit(guildxoxoxoxid: int, rolexoxoxoxid: int, maxxoxoxoxentries: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO giveaway_limits (guildxoxoxoxid, rolexoxoxoxid, maxxoxoxoxentries) VALUES (?, ?, ?)
            ON CONFLICT(guildxoxoxoxid, rolexoxoxoxid) DO UPDATE SET maxxoxoxoxentries = excluded.maxxoxoxoxentries
        """, (guildxoxoxoxid, rolexoxoxoxid, maxxoxoxoxentries))
        await db.commit()

async def getxoxoxoxgiveawayxoxoxoxlimits(guildxoxoxoxid: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT rolexoxoxoxid, maxxoxoxoxentries FROM giveaway_limits WHERE guildxoxoxoxid = ?", (guildxoxoxoxid,)) as cursor:
            return await cursor.fetchall()