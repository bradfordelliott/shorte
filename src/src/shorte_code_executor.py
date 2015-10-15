import re
import subprocess
import string
import shlex

from shorte_defines import *

class code_result_t(object):
    def __init__(self):
        self.run_rc = None
        self.run_result = None
        self.run_result_image = None
        self.compile_result = None
        self.compile_rc = None


    def has_run_rc(self):
        if(None != self.run_rc):
            return True
        return False
    def get_run_rc(self):
        return self.run_rc
    def set_run_rc(self, rc):
        self.run_rc = rc

    def has_run_result(self):
        if(None != self.run_result):
            return True
        return False
    def get_run_result(self):
        return self.run_result
    def set_run_result(self, result):
        self.run_result = result
    
    def has_compile_rc(self):
        if(None == self.compile_rc):
            return False
        return True
    def get_compile_rc(self):
        return self.compile_rc
    def set_compile_rc(self, rc):
        self.compile_rc = rc

    def has_compile_result(self):
        if(None != self.compile_result and (len(self.compile_result.strip()) > 0)):
            return True
        return False
    def get_compile_result(self):
        return self.compile_result
    def set_compile_result(self, result):
        self.compile_result = result


    def has_image(self):
        if(None != self.run_result_image):
            return True
        return False
    def get_image(self):
        return self.run_result_image
    def set_image(self, result):
        self.run_result_image = result

class CompileException(Exception):
    def __init__(self, rc, message):
        Exception.__init__(self, message)
        self.rc = rc
        self.message = message

class RunException(Exception):
    def __init__(self, rc, message):
        Exception.__init__(self, message)
        self.rc = rc
        self.message = message

class code_executor_t:
    def __init__(self):

        self.m_blah = 0

    def push_file(self, source, modifiers):

        machine = ""
        port = ""

        if(modifiers.has_key("machine")):
            machine = modifiers["machine"]

        if(modifiers.has_key("port")):
            port = modifiers["port"]

        output = "/tmp/%s" % os.path.basename(source)

        cmd = "scp -P %s %s %s:%s" % (port, source, machine, output)
        os.popen(cmd).read()

        return output

    def source_file_name(self, language):

        extension = {}
        extension["perl"] = "pl"
        extension["python"] = "py"
        extension["java"] = "java"
        extension["c"] = "c"
        extension["cpp"] = "cpp"
        extension["d"] = "d"
        extension["bash"] = "sh"
        extension["vera"] = "vr"
        extension["verilog"] = "sv"
        extension["tcl"] = "tcl"
        extension["batch"] = "cmd"
        extension["swift"] = "swift"
        extension["go"] = "go"
        extension["javascript"] = "js"

        name = "tmpexample.%s" % extension[language]

        return name

    def create_source_file(self, language, path, source, prefix=""):

        #print("Creating %s, language=%s, source=%s" % (path, language, source))
        
        if(language in ("python", "perl", "bash", "java", "c", "cpp", "vera", "verilog", "tcl", "batch", "swift", "go", "javascript")):

            handle = open(path, "wt")

            if(language == "bash"):
                source = "#!/usr/bin/env bash\n" + source

            handle.write(source)
            handle.close()

            return True

        
        return False
        
        

    def execute(self, language, source, modifiers):

        cresult = code_result_t()

        if(not modifiers.has_key("exec")):
            return cresult

        if(modifiers["exec"] == "0" or modifiers["exec"] == "no"):
            return cresult

        machine = ""
        port = "22"
        run_args = ""
        compile_args = ""
        
        if(modifiers.has_key("machine")):
            machine = modifiers["machine"]
        if(modifiers.has_key("port")):
            port = modifiers["port"]
        if(modifiers.has_key("run_args")):
            run_args = modifiers["run_args"]
        if(modifiers.has_key("compile_args")):
            compile_args = modifiers["compile_args"]
            
        exec_prefix = ""
        if(platform.system() == "Windows"):
            exec_prefix = ""
        elif(platform.platform() == "Cygwin"):
            exec_prefix = "./"
        else:
            exec_prefix = "./"

        #print "exec = %s" % exec_prefix
        #print platform.system()

        #source_file = os.getcwd() + os.sep + self.source_file_name(language)
        source_file = self.source_file_name(language)
        #print "Source file = %s" % source_file

        keep_source_file = False
        if(modifiers.has_key("save")):
            source_file = modifiers["save"]
            keep_source_file = True
        elif(modifiers.has_key('name')):
            source_file = modifiers['name']

        image_file = None
        if(modifiers.has_key('save_image')):
            image_file = modifiers['save_image']
            
        if(language == "python"):
            if(modifiers.has_key('path_add_shorte')):
                prefix_path = shorte_get_startup_path()
                source = '''import sys\nsys.path.append("%s")\n\n%s''' % (prefix_path, source)


        # Create the temporary source file
        self.create_source_file(language, source_file, source)

        try:
            if(language in ('python', 'perl', 'tcl', 'bash', 'swift', 'go', 'javascript')):

                if(language == "bash"):
                    if("Windows" == platform.system()):
                        raise RunException(-1, "bash not currently supported under windows")
                elif(language == "swift"):
                    if("Darwin" != platform.system()):
                        raise RunException(-1, "swift not currently supported on platforms other than OSX")
                elif(language == "go"):
                    if("Darwin" != platform.system()):
                        raise RunException(-1, "go not currently supported on platforms other than OSX")
                elif(language == "javascript"):
                    if("Darwin" != platform.system()):
                        raise RunException(-1, "javascript not currently supported on platforms other than OSX")

                if(machine != ""):
                    cmd_copy = "scp -P %s %s %s:/tmp/." % (port, source_file, machine)
                    #print cmd_copy
                    os.popen(cmd_copy)

                    #result = os.popen("%s tmpexample.py 2>&1" % python).read();
                    cmd_run = "ssh -p %s %s \"%s /tmp/%s 2>&1\"" % (port, machine, g_tools.get_python(), source_file)
                    #print cmd_run

                    result = os.popen(cmd_run).read()
                else:
                    cmd_run = string.Template(shorte_get_config(language, "run", expand_os=True)).substitute({
                        "source" : source_file})

                    cmd_run = cmd_run.split(" ")

                    if(len(run_args) > 0):
                        cmd_run.extend(shlex.split(run_args))

                    rc = -1
                    try:
                        phandle = subprocess.Popen(cmd_run, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        result = phandle.stdout.read()
                        result += phandle.stderr.read()
                        phandle.wait()
                        rc = phandle.returncode
                    except:
                        raise CompileException(rc, "Failed running %s example" % language)

                    cresult.set_run_result(result)
                    cresult.set_run_rc(rc)
                    
                    #result = os.popen("%s %s 2>&1" % (g_tools.get_python(), source_file)).read();
            
            elif(language in ("c", "cpp")):
               
                compiler = g_tools.get_c_compiler()

                if(machine != ""):
                    cmd_copy = "scp -P %s %s %s:/tmp/." % (port, source_file, machine)
                    #print cmd_copy
                    handle = os.popen(cmd_copy)
                    result = handle.read()
                    rc = handle.wait()
                    #print "COPY: %s" % result

                    cmd_compile = "ssh -p %s %s \"%s -o /tmp/tmpexample /tmp/%s 2>&1\"" % (port, machine, compiler, source_file)
                    #print cmd_compile
                    result += os.popen(cmd_compile).read()
                    #print result
                    
                    cmd_run = "ssh -p %s %s \"/tmp/%s 2>&1\"" % (port, machine, "tmpexample")
                    result += os.popen(cmd_run).read()

                else:
                    #print os.getcwd()
                    cmd_compile = string.Template(shorte_get_config(language, "compile", expand_os=True)).substitute({
                        "output" : "tmpexample3",
                        "source" : source_file})

                    cmd_compile = shlex.split(cmd_compile)
                    
                    if(len(compile_args) > 0):
                        cmd_compile.extend(shlex.split(compile_args))

                    phandle = subprocess.Popen(cmd_compile, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    result = phandle.stdout.read()
                    result += phandle.stderr.read()
                    phandle.wait()
                    rc = phandle.returncode

                    cresult.set_compile_result(result)
                    cresult.set_compile_rc(rc)

                    if(rc != 0):
                        raise CompileException(rc, result)
                        
                    #phandle.close()
                    #print "Compile result = [%s]" % result
                    
                    cmd_run = ["%stmpexample3" % exec_prefix]
                    if(len(run_args) > 0):
                        cmd_run.extend(shlex.split(run_args))

                    phandle = subprocess.Popen(cmd_run, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    result = phandle.stdout.read()
                    result += phandle.stderr.read()
                    phandle.wait()
                    rc = phandle.returncode

                    cresult.set_run_result(result)
                    cresult.set_run_rc(rc)
                    
                    # Make sure we cleanup the temporary executable after we're done
                    try:
                        os.unlink('%s/tmpexample3' % exec_prefix)
                    except:
                        pass
                    #print "Run result = [%s]" % result
                    #print "Run Returns = ", rc
            
            elif(language == "java"):

                basename = os.path.basename(source_file)
                class_name = re.sub(".java", "", basename)

                #print "Class = %s" % class_name
                #print "Base  = %s" % basename
               
                compiler = "javac"
                runtime = "java"
                #g_tools.get_java_compiler()

                if(machine != ""):

                    remote_file = self.push_file(source_file, modifiers) 

                    cmd_compile = "ssh -p %s %s \"%s %s 2>&1\"" % (port, machine, compiler, remote_file)
                    result = os.popen(cmd_compile).read()

                    cmd_run = "ssh -p %s %s \"%s -cp /tmp %s 2>&1\"" % (port, machine, runtime, class_name)
                    result += os.popen(cmd_run).read()

                    # Clean up any output files
                    os.popen("ssh -p %s %s \"rm -rf /tmp/%s.class\"" % (port, machine, class_name))
                    os.popen("ssh -p %s %s \"rm -rf /tmp/%s\"" % (port, machine, source_file))

                else:
                    (class_file,ext) = os.path.splitext(source_file)
                    #print "JAVA"
                    #print "  source: %s" % source_file
                    #print "  class:  %s" % class_file

                    # The compile command
                    cmd_compile = string.Template(shorte_get_config("java", "compile", expand_os=True)).substitute({
                        "source" : source_file})

                    # The run command
                    cmd_run = string.Template(shorte_get_config("java", "run", expand_os=True)).substitute({
                        "source" : class_file})

                    cmd_compile = cmd_compile.split(" ")
                    cmd_run     = cmd_run.split(" ")

                    if(len(run_args) > 0):
                        cmd_run.extend(shlex.split(run_args))
                    if(len(compile_args) > 0):
                        cmd_compile.extend(shlex.split(compile_args))

                    # First compile the application
                    rc = -1
                    try:
                        phandle = subprocess.Popen(cmd_compile, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        result = phandle.stdout.read()
                        result += phandle.stderr.read()
                        phandle.wait()
                        rc = phandle.returncode

                        cresult.set_compile_result(result)
                        cresult.set_compile_rc(rc)
                    except:
                        raise CompileException(rc, "Failed running java compiler")

                    if(0 != rc):
                        raise CompileException(rc, result)
                    
                    # Now run the application
                    phandle = subprocess.Popen(cmd_run, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    result = phandle.stdout.read()
                    result += phandle.stderr.read()
                    phandle.wait()
                    rc = phandle.returncode

                    cresult.set_run_result(result)
                    cresult.set_run_rc(rc)
                    
                    # Make sure we remove any .class files
                    try:
                        os.unlink("%s.class" % class_file)
                    except:
                        pass

                    if(0 != rc):
                        raise RunException(rc,result)

                    #result = os.popen("%s tmpexample.java 2>&1" % compiler).read();
                    #print "result = %s" % result
                    #result = os.popen("%stmpexample 2>&1" % exec_prefix).read();
                    #print "result = %s" % result
       
            elif(language == "d"):
                # Run the python interpreter to get an answer
                tmp = open("tmpexample.d", "w")
                tmp.write(source)
                tmp.close()
                result = os.popen("%s -o tmpexample tmpexample.d 2>&1" % gdc).read();
                result += os.popen("%stmpexample" % exec_prefix).read();

            elif(language == "vera"):

                # Run the python interpreter to get an answer
                tmp = open(source_file, "w")
                tmp.write(source)
                tmp.close()

                if(machine != ""):

                    cmd_copy = "scp -P %s %s %s:/tmp/." % (port, source_file, machine)
                    os.popen(cmd_copy)

                    cmd_run = "ssh -p %s %s \"module load vcs && module load scl && vcs -R -ntb /tmp/%s 2>&1\"" % (port, machine, source_file)

                    result = os.popen(cmd_run).read()

                    # Parse the output of the vera compiler in order to 
                    expr = re.compile("(.*?Runtime version.*?\n)(.*?)\$finish.*", re.DOTALL)

                    result = expr.sub("\\2", result)

                else:
                    raise Exception("Cannot execute vera on local machine")
            
            elif(language == "verilog"):

                # Run the python interpreter to get an answer
                tmp = open(source_file, "w")
                tmp.write(source)
                tmp.close()

                if(machine != ""):

                    cmd_copy = "scp -P %s %s %s:/tmp/." % (port, source_file, machine)
                    os.popen(cmd_copy)

                    cmd_run = "ssh -p %s %s \"module load vcs && module load scl && vcs -R -ntb /tmp/%s 2>&1\"" % (port, machine, source_file)

                    result = os.popen(cmd_run).read()

                    # Parse the output of the vera compiler in order to 
                    expr = re.compile("(.*?Runtime version.*?\n)(.*?)\$finish.*", re.DOTALL)

                    result = expr.sub("\\2", result)

                else:
                    raise Exception("Cannot execute verilog on local machine")

            elif(language == "batch"):
                
                if("windows" != platform.system()):
                    raise RunException(-1, "batch not currently supported on platforms other than Windows")

                # Run the batch file using cmd /c
                tmp = open(source_file, "w")
                tmp.write(source)
                tmp.close()

                cmd_run = "cmd /c %s" % source_file

                result = os.popen(cmd_run).read()

                #print "RESULT=[%s]" % result

        except RunException as e:
            cresult.set_run_result(e.message)
            cresult.set_run_rc(e.rc)
            return cresult
        except CompileException as e:
            cresult.set_compile_result(e.message)
            cresult.set_compile_rc(e.rc)
            return cresult
        finally: 

            # Now that we're done with the file make sure we
            # remove the source file so we don't clutter up the
            # working directory
            if(not keep_source_file):
                os.unlink(source_file)

        #self.m_example_id += 1
        #example_name = "example_%d" % self.m_example_id
        #shutil.copy("tmpexample.py", self.m_output_directory + "/" + example_name)

        if(image_file != None and (not os.path.exists(image_file))):
            ERROR("Image file %s was not created for some reason" % image_file)
            image_file = None
            rc = -1

        cresult.set_image(image_file)

        return cresult

