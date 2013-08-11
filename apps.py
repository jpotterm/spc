import re
import sys, os

# using convention over configuration 
# the executable is the name of the app
# and the input file is the name of the app + '.in'
apps_dir = 'apps'
sim_fn = 'mendel.in'
user_dir = 'user_data'
# end set 

# future feature
#workflow = "login >> start >> confirm >> execute"

# define user input parameters here and set them with default values
#params = dict(case_id='xyz123',mutn_rate=10,frac_fav_mutn=0.00001,
#              reproductive_rate=2,pop_size=100,num_generations=50)

# define parameters for executing simulation
#exe = dict(path='engine/mendel')

# user must write their own function for how to write the output file
class app_f90(object):
    '''Class for plugging in Fortran apps ...'''
    
    def __init__(self,appname):
        self.appname = appname
	self.outfn = appname + '.out'
        self.user_dir = user_dir + os.sep + self.appname
        self.params, self.blockmap, self.blockorder = self.read_params()
        self.exe = apps_dir + os.sep + self.appname + os.sep + self.appname

    def write_params(self,form_params):
        '''write the input file needed for the simulation'''

        sim_dir = self.user_dir + os.sep + form_params['case_id'] + os.sep
        #form_params['data_file_path'] = sim_dir
        form_params['data_file_path'] = "'./'"
       
        if not os.path.exists(sim_dir):
            os.makedirs(sim_dir)

        cid = form_params['case_id']
        #fn = user_dir + os.sep + cid + os.sep + sim_fn
        fn = self.user_dir + os.sep + cid + os.sep + sim_fn

        f = open(fn, 'w')
        # need to know what attributes are in what blocks
        for block in self.blockorder:
            f.write("&%s\n" % block)
            for key in self.blockmap[block]:
                # if the keys are not in the params, it means that
                # the checkboxes were not checked, so add the keys
                # to the form_params here and set the values to False
                if key not in form_params:
                    form_params[key] = "F"  

                # detect strings and enclose with single quotes
                m = re.search(r'[a-zA-Z]{2}',form_params[key])
                if m:
                    if not re.search('[0-9.]*e+[0-9]*|[FT]',m.group()):
                        form_params[key] = "'" + form_params[key] + "'"

                f.write(key + ' = ' + form_params[key] + "\n")
            f.write("/\n\n")
        f.close
        return 1

    # student - needs to modify reader and writer so that can handle
    # multiple values for each parameter
    def read_params(self,cid='TMPLET'):
        '''read the namelist file and return as a dictionary'''
        fn = self.user_dir + os.sep + cid + os.sep + sim_fn
        params = dict()
        blockmap = dict() 
        blockorder = []
        for line in open(fn, 'rU'):
            m = re.search(r'&(\w+)',line) # block title
            n = re.search(r'(\w+) = (.*$)',line) # parameter
            if m:
                block = m.group(1)  
                blockorder += [ m.group(1) ]
            elif n:
                # Delete apostrophes and commas
                val = re.sub(r"[',]", "", n.group(2))
                # Delete Fortran comments and whitespace
                params[n.group(1)] = re.sub(r'\!.*$', "", val).strip()
                # Append to blocks e.g. {'basic': ['case_id', 'mutn_rate']}
                blockmap.setdefault(block,[]).append(n.group(1))
		#print n.group(1), val
        return params, blockmap, blockorder
    # convert some into dropdown boxes

    def write_html_template(self):
    # need to output according to blocks
        confirm="/confirm"
        f = open('views/start.tpl', 'w')
        f.write("%include header title='confirm'\n")
        f.write("<body onload=\"init()\">\n")
        f.write("%include navbar\n")
        f.write("<!-- This file was autogenerated from CloudThrust -->\n")
        f.write("<form action=\""+confirm+"\" method=\"post\">\n")
        f.write("<input class=\"start\" type=\"submit\" value=\"confirm\" />\n")
        f.write("<input type=\"hidden\" name=\"app\" value=\"{{app}}\"/>\n")
        f.write("<div class=\"tab-pane\" id=\"tab-pane-1\">\n")
        for block in self.blockorder:
            f.write("<div class=\"tab-page\">\n")
            f.write("<h2 class=\"tab\">" + block + "</h2>\n")
            f.write("<table><tbody>\n")
            for param in self.blockmap[block]:
                str = "<tr><td>" + param + ":</td>\n"
                str += "<td>"
                if re.search("[TF]",self.params[param]):
                    str += "<input type=\"checkbox\" name=\"" + param + "\" "
                    str += "value=\"true\"/>"
                else: 
                    str += "<input type=\"text\" name=\"" + param + "\" "
                    str += "value=\"{{" + param + "}}\"/>"
                str += "</td></tr>\n"
                f.write(str)
            f.write("</tbody></table>\n")
            f.write("</div>\n")
        f.write("</div>\n")
        f.write("</form>\n")
        f.write("%include footer")
        f.close()
        return 1
