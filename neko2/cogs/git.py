"""
Allows the bot owner to update the bot using Git, if it is installed.
"""
import asyncio
import io
import os
import shutil
import traceback


from neko2.engine import commands
from neko2.shared import fsa
from neko2.shared import traits


class GitCog(traits.Scribe, traits.CpuBoundPool):

    @commands.is_owner()
    @commands.command(
        brief='Updates the bot if we are in a valid git repository.',
        hidden=True)
    async def update(self, ctx):
        """
        This will DM you the results.

        The following assumptions are made:
          - The current system user has permission to modify the `.git`
            directory, and modify the contents of this directory.
          - That git is installed.
          - That the current working directory contains the `.git` directory.
        """
        # Ensure git is installed first
        git_path = shutil.which('git')

        if not git_path:
            return await ctx.author.send('I can\'t seem to find git!')

        # Ensure that we have a `.git` folder in the current directory
        if os.path.exists('.git'):
            if os.path.isdir('.git'):
                pass
            else:
                return await ctx.author.send('.git is not a directory')
        else:
            return ctx.author.send('.git does not exist. Is this a repo?')

        with io.StringIO() as out_s:
            shell = os.getenv('SHELL', None)
            if shell is None:
                shell = shutil.which('sh')
                if shell is None:
                    shell = '?? '

            async def call(cmd):
                out_s.write(f'{shell} -c {cmd}')
                process = await asyncio.create_subprocess_shell(
                    cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE)
                out_s.write(f'Invoked PID {process.pid}\n')
                # Might deadlock?
                out_s.write((await process.stdout.read()).decode())
                out_s.write((await process.stderr.read()).decode())
                await process.terminate()
                await process.wait()
                out_s.write(f'Terminated with code {process.returncode}\n')


            try:
                call('git status --porcelain --ignored --verbose')

                # Check if existing stashes exist
                if os.path.exists(os.path.join('.git', 'refs', 'stash')):
                    out_s.write('Warning: stashes already exist')
                    call('git stash list')

                await call(f'{git_path} stash\n')
                await call(f'{git_path} pull --all --squash --verbose --stat\n')
                await call(f'{git_path} stash apply\n')
                await call(f'{git_path} diff HEAD HEAD~1 --stat\n')
            except BaseException as ex:
                err = traceback.format_exception(type(ex), ex, ex.__traceback__)
                # Seems that lines might have newlines. This is annoying.

                err = ''.join(err).split('\n')
                err = [f'# {e_ln}\n' for e_ln in err]

                # Remove last comment.
                err = ''.join(err)[:-1]
                out_s.write(err)
                traceback.print_exception(type(ex), ex, ex.__traceback__)
            finally:
                log = out_s.getvalue()

                self.logger.warning(
                    f'{ctx.author} Invoked update from '
                    f'{ctx.guild}@#{ctx.channel}\n{log}')

                pag = fsa.Pag(prefix='```bash', suffix='```')

                for line in log.split('\n'):
                    pag.add_line(line)

                await ctx.author.send(
                    f'Will send {len(pag.pages)} messages of output!')

                for page in pag.pages:
                    await ctx.author.send(page)


def setup(bot):
    bot.add_cog(GitCog())
