#****************************************************************************
#* sim_verilator.py
#*
#* Copyright 2023 Matthew Ballance and Contributors
#*
#* Licensed under the Apache License, Version 2.0 (the "License"); you may 
#* not use this file except in compliance with the License.  
#* You may obtain a copy of the License at:
#*
#*   http://www.apache.org/licenses/LICENSE-2.0
#*
#* Unless required by applicable law or agreed to in writing, software 
#* distributed under the License is distributed on an "AS IS" BASIS, 
#* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  
#* See the License for the specific language governing permissions and 
#* limitations under the License.
#*
#* Created on:
#*     Author: 
#*
#****************************************************************************
import os
import subprocess
from pytest_fv import HdlSim, ToolRgy, ToolKind
from .sim_vlog_base import SimVlogBase

class SimVerilator(SimVlogBase):

    def __init__(self):
        super().__init__()

    def build(self, build_args : HdlSim.BuildArgs):
        src_l, cpp_l, inc_s, def_m = self._getSrcIncDef(build_args)

        cmd = [
            'verilator', '--binary', '-sv', '-o', 'simv'
        ]

        for inc in inc_s:
            cmd.append('+incdir+%s' % inc)

        for key,val in def_m.items():
            if val is None or val == "":
                cmd.append("+define+%s" % key)
            else:
                cmd.append("+define+%s=%s" % (key, val))

        for top in build_args.top:
            cmd.append('--top-module')
            cmd.append(top)

        if len(src_l) == 0:
            raise Exception("No source files specified")

        for vsrc in src_l:
            cmd.append(vsrc)


        logfile = build_args.logfile
        if not os.path.isabs(logfile):
            logfile = os.path.join(build_args.builddir, logfile)

        print("cmd: %s" % str(cmd))
        with open(logfile, "w") as log:
            log.write("** Compile\n")
            log.write("** Command: %s\n" % str(cmd))
            log.flush()
            res = subprocess.run(
                cmd, 
                cwd=build_args.builddir,
                stderr=subprocess.STDOUT,
                stdout=log)
            
            if res.returncode != 0:
                raise Exception("Compilation failed")

        if len(cpp_l) > 0:
            print("TODO: need to compile DPI")

    def run(self, run_args : HdlSim.RunArgs):
        cmd = [ os.path.join(run_args.builddir, "obj_dir", "simv") ]

        logfile = run_args.logfile
        if not os.path.isabs(logfile):
            logfile = os.path.join(run_args._rundir, logfile)

        with open(logfile, "w") as log:
            log.write("** Command: %s\n" % str(cmd))
            log.write("** CWD: %s\n" % run_args._rundir)
            log.flush()
            res = subprocess.run(
                cmd,
                cwd=run_args._rundir,
                env=run_args.env,
                stderr=subprocess.STDOUT,
                stdout=log)
            
            if res.returncode != 0:
                raise Exception("Run failed")

        pass


ToolRgy.register(ToolKind.Sim, "vl", SimVerilator)
