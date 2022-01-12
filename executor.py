from .. import loader, utils
from meval import meval

import asyncio
import builtins

def register(cb):
    cb(ExecutorMod())

class ExecutorMod(loader.Module):
    """Execute commands"""
    strings = {"name": "Executor",
                        "no_args": "<strong>Invalid arguments</strong>",
                        "not_found": "<strong>Command not found</strong>"}
    
    exceptions = ["code", "globs", "kwargs"]
    
    class FakeCommand:
        def __init__(self, message, name, command):
            self.context = message
            self.name = name
            self.command = command
         
        async def __call__(self, *args):
            msg = ".%s %s" % (self.name, " ".join(map(str, args)))
            reply = await self.context.get_reply_message()
            if reply:
                event = await reply.reply(msg)
            else:
                event = await self.context.respond(msg)
            await self.command(event)

    async def excmd(self, message):
        """ex [count] [command] [args...]"""
        args = message.raw_text.split(" ", maxsplit=3)
        
        if len(args) < 3:
            await utils.answer(message, self.strings["no_args"])
            return
        
        if args[2] in self.allmodules.aliases.keys():
            command = self.allmodules.commands[self.allmodules.aliases[args[2]]]
        elif args[2] in self.allmodules.commands.keys():
            command = self.allmodules.commands[args[2]]
        else:
            await utils.answer(message, self.strings["not_found"])
            return
        
        reply = await message.get_reply_message()
        for i in range(int(args[1])):
            msg = "." + " ".join(args[2:]).format(n=i)
            if reply:
                event = await reply.reply(msg)
            else:
                event = await message.respond(msg)
            await command(event)

    async def plcmd(self, message):
        """pl [code]"""
        arg = utils.get_args_raw(message)
                
        env = {"message": message}
        for name, cmd in self.allmodules.commands.items():
            if name in self.exceptions or hasattr(builtins, name):
                name = "_" + name
            env[name] = self.FakeCommand(message, name, cmd)
           
        for name, source in self.allmodules.aliases.items():
            if name in self.exceptions or hasattr(builtins, name):
                name = "_" + name
            env[name] = self.FakeCommand(message, name, self.allmodules.commands[source])
            
        await meval(arg, globals(), **env)
    
    async def echocmd(self, message):
        """echo [text]"""
        await utils.answer(message, utils.get_args_raw(message))
    