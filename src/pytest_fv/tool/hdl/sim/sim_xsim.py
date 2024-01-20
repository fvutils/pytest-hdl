#****************************************************************************
#* sim_xsim.py
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

class SimXsim(SimVlogBase):

    def __init__(self):
        super().__init__()
        pass

    def build(self, build_args : HdlSim.BuildArgs):
        src_l, cpp_l, inc_s, def_m = self._getSrcIncDef(build_args)

        cmd = [
            'xvlog', "-sv"
        ]

        if self.hasFlag("sv-uvm"):
            cmd.extend(["-L", "uvm"])

        for inc in inc_s:
            cmd.append('-i')
            cmd.append(inc)

        for key,val in def_m.items():
            cmd.append("-d")
            if val is None or val == "":
                cmd.append(key)
            else:
                cmd.append("%s=%s" % (key, val))

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

        cmd = [ 'xelab' ]
#        '--relax',  '--snapshot', 'snap' ]

        if len(build_args.top) == 0:
            raise Exception("Must specify root module")

        for top in build_args.top:
            cmd.append(top)
        cmd.extend(['-relax', '-s', 'top', '-timescale', '1ns/1ps'])
        print("cmd: %s" % str(cmd))
        with open(logfile, "a") as log:
            log.write("** Elab\n")
            log.flush()
            res = subprocess.run(
                cmd, 
                cwd=build_args.builddir,
                stderr=subprocess.STDOUT,
                stdout=log)

            if res.returncode != 0:
                raise Exception("Compilation failed")

    def run(self, run_args : HdlSim.RunArgs):
        cmd = [ 'xsim', '--runall']

        cmd.append('top')

        logfile = run_args.logfile
        if not os.path.isabs(logfile):
            logfile = os.path.join(run_args._rundir, logfile)

        with open(logfile, "w") as log:
            res = subprocess.run(
                cmd,
                cwd=run_args._rundir,
                env=run_args.env,
                stderr=subprocess.STDOUT,
                stdout=log)
            
            if res.returncode != 0:
                raise Exception("Run failed")

        pass


ToolRgy.register(ToolKind.Sim, "xsm", SimXsim)

