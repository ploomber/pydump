#*****************************************************************************
# Copyright (C) 2001 Nathaniel Gray <n8gray@caltech.edu>
# Copyright (C) 2001-2004 Fernando Perez <fperez@colorado.edu>
# Copyright (C) 2022 Eduardo Blancas <eduardo@ploomber.io>
#
# Distributed under the terms of the BSD License.  The full license is in
# the file COPYING, distributed as part of this software.
#*****************************************************************************
import sys
import types

from IPython.core.display_trap import DisplayTrap

from pydump.pydump import save_dump


# NOTE: this is based on the IPython implementation
def debugger(self, force: bool = False):
    if force or self.call_pdb:
        if self.pdb is None:
            self.pdb = self.debugger_cls()
        # the system displayhook may have changed, restore the original
        # for pdb
        display_trap = DisplayTrap(hook=sys.__displayhook__)
        with display_trap:
            self.pdb.reset()
            # Find the right frame so we don't pop up inside ipython itself
            if hasattr(self, 'tb') and self.tb is not None:
                etb = self.tb
            else:
                etb = self.tb = sys.last_traceback
            while self.tb is not None and self.tb.tb_next is not None:
                assert self.tb.tb_next is not None
                self.tb = self.tb.tb_next
            if etb and etb.tb_next:
                etb = etb.tb_next
            self.pdb.botframe = etb.tb_frame

            print('Dump stored at ipython.dump')
            save_dump('ipython.dump', etb)
            # self.pdb.interaction(None, etb)

        if hasattr(self, 'tb'):
            del self.tb


def patch_ipython():
    # optional dependency
    import IPython
    term = IPython.get_ipython()
    term.run_line_magic('pdb', 'on')
    term.InteractiveTB.debugger = types.MethodType(debugger,
                                                   term.InteractiveTB)