#!/usr/bin/env python
import sys, os, shutil, urllib2, time
if os.path.exists("src/config.py"):
    from src import config, uploads
    from src import apps as appmod
import xml.etree.ElementTree as ET
import hashlib, re

sys.argv[1:]

url = 'https://s3-us-west-1.amazonaws.com/scihub'

def usage():
    buf =  "usage: spc <command> [options]\n\n"
    buf += "available commands:\n"
    buf += "init     initialize database and create basic config.py file\n"
    buf += "go       start the server\n"
    buf += "install  install an app\n"
    #buf += "list     list installed or available apps\n"
    #buf += "search   search for available apps\n"
    #buf += "test     run unit tests\n"
    return buf

if (len(sys.argv) == 1):
    print usage()
    sys.exit()

#db = config.db

def create_config_file():
    """Create a config.py file in the spc directory"""
    fn="src/config.py"
    if not os.path.exists(fn):
        with open(fn, "w") as f:
            f.write("# USER AUTHENTICATION\n")
            f.write("auth = False\n")
            f.write("configurable = True\n")
            f.write("\n# the number of lines to show while monitoring\n")
            f.write("tail_num_lines = 24\n")
            f.write("\n# the number of rows to show at a time in the jobs table\n")
            f.write("jobs_num_rows = 20\n")
            f.write("\n# DATABASE\n")
            f.write("db = 'spc.db'\n")
            f.write("dbdir = 'db'\n")
            f.write("uri = 'sqlite://'+db\n")
            f.write("\n# DIRECTORIES\n")
            f.write("apps_dir = 'apps'\n")
            f.write("user_dir = 'user_data'\n")
            f.write("upload_dir = '_uploads'\n")
            f.write("tmp_dir = 'static/tmp'\n")
            f.write("mpirun = '/usr/local/bin/mpirun'\n")
            f.write("\n# SCHEDULER\n")
            f.write("# uniprocessor scheduling -- for single-core machines\n")
            f.write("sched = 'uni'\n")
            f.write("# schedule more than one job at a time (multiprocessor)\n")
            f.write("#sched = 'mp'\n")
            f.write("default_priority = 3\n")
            f.write("# number of processors available to use on this machine\n")
            f.write("np = 2\n")
            f.write("\n# WEB SERVER\n")
            f.write("# don't define server if you want to use built-in\n")
            f.write("# other options: cherrypy, bjoern, tornado, gae, etc.\n")
            f.write("# cherrypy is a decent multi-threaded server\n")
            f.write("#server = 'cherrypy'\n")
            f.write("# port number to listen for connections\n")
            f.write("port = 8580\n")

def initdb():
    """Initializes database file"""
    from src import config
    from src import model2
    # somehow the following doesn't work properly

    # create db directory if it doesn't exist
    if not os.path.exists(config.dbdir):
        os.makedirs(config.dbdir)
    # make a backup copy of db file if it exists

    #if os.path.isfile(db): 
    #    print "ERROR: a database file already exists, please rename it and rerun"
    #    sys.exit()
    #    shutil.copyfile(db, db+".bak")

    # get rid of old .table files
    for f in os.listdir(config.dbdir):
        if re.search("\.table", f):
            print "removing file:", f
            os.remove(os.path.join(config.dbdir, f))
    # delete previous .db file should back first (future)
    dbpath = os.path.join(config.dbdir, config.db)
    if os.path.isfile(dbpath): os.remove(dbpath)
    # create db
    dal = model2.dal(uri=config.uri,migrate=True)
    # add guest and admin user
    hashpw = hashlib.sha256("guest").hexdigest()
    dal.db.users.insert(user="guest",passwd=hashpw)
    hashpw = hashlib.sha256("admin").hexdigest()
    dal.db.users.insert(user="admin",passwd=hashpw)
    # add default app
    dal.db.apps.insert(name="dna",description="Compute reverse complement," +\
                       "GC content, and codon analysis of given DNA string.", 
                       category="bioinformatics",
                       language="python",  
                       input_format="namelist", 
                       command="../../../../apps/dna/dna")
    dal.db.plots.insert(id=1,appid=1,ptype="flot-cat",title="Dinucleotides")
    dal.db.plots.insert(id=2,appid=1,ptype="flot-cat",title="Nucleotides")
    dal.db.plots.insert(id=3,appid=1,ptype="flot-cat",title="Codons")
    dal.db.datasource.insert(filename="din.out",cols="1:2",pltid=1)
    dal.db.datasource.insert(filename="nucs.out",cols="1:2",pltid=2)
    dal.db.datasource.insert(filename="codons.out",cols="1:2",pltid=3)
    #dal.db.disciplines.insert(name="Chemistry")
    #dal.db.disciplines.insert(name="Linguistics")
    #dal.db.disciplines.insert(name="Finance")
    #dal.db.disciplines.insert(name="Biology")
    #dal.db.disciplines.insert(name="Physics")
    #dal.db.disciplines.insert(name="Fluid Dynamics")
    #dal.db.disciplines.insert(name="Geodynamics")
    #dal.db.disciplines.insert(name="Molecular Dynamics")
    #dal.db.disciplines.insert(name="Weather Prediction")
    # write changes to db
    dal.db.commit()

notyet = "this feature not yet working"

# http://stackoverflow.com/questions/4028697/how-do-i-download-a-zip-file-in-python-using-urllib2
def dlfile(url):
    # Open the url
    try:
        f = urllib2.urlopen(url)
        print "downloading " + url
        # Open our local file for writing
        with open(os.path.basename(url), "wb") as local_file:
            local_file.write(f.read())
    #handle errors
    except urllib2.HTTPError, e:
        print "HTTP Error:", e.code, url
    except urllib2.URLError, e:
        print "URL Error:", e.reason, url

# process command line options
if __name__ == "__main__":
    if (sys.argv[1] == "init"):
        create_config_file()
        print "creating database."
        initdb()
    elif (sys.argv[1] == "go"):
        os.system("python src/main.py")
    elif (sys.argv[1] == "search"):
        print notyet
    elif (sys.argv[1] == "test"):
        os.chdir('tests')  
        os.system("python test_unit.py")
    elif (sys.argv[1] == "install"):
        install_usage = "usage: spc install /path/to/file.zip\n    or spc install http://url/to/file.zip"
                
        if len(sys.argv) == 3:

            if re.search(r'http://*$', sys.argv[2]):
                # download zip file into apps folder
                durl = url+'/'+sys.argv[2]
                print 'durl is:',durl
                dlfile(durl)

            save_path = sys.argv[2]
            app_dir_name = os.path.basename(save_path).split('.')[0]
            if os.path.isfile(app_dir_name):
                print 'ERROR: app directory exists already. Please remove first.'
                sys.exit()
            # don't overwrite another directory if it exists
            # instead rename old redirectory with timestamp
            if os.path.isfile(app_dir_name):
                timestr = time.strftime("%Y%m%d-%H%M%S")
                shutil.move(app_dir_name,app_dir_name+"."+timestr)

            # unzip file
            import zipfile
            fh = open(save_path, 'rb')
            z = zipfile.ZipFile(fh)
            z.extractall()
            fh.close()

            # read the json app config file and insert info into db
            import json
            from src import model2
            path = app_dir_name + os.sep + "spc.json"
            print path
            with open(path,'r') as f: 
                data = f.read()
            print data
            parsed = json.loads(data)
            print parsed

            # get name of app from json data
            app = parsed['name']
            app_path = config.apps_dir + os.sep + app

            # move directory to apps folder
            shutil.move(app_dir_name,app_path)

            # connect to db
            #os.chdir(os.pardir)
            dal = model2.dal(uri=config.uri) 

            # check if app already exists before preceding
            result = dal.db(dal.db.apps.name==parsed['name']).select().first()
            if result: 
                print "\n*** ERROR: app already exists in database ***"
                shutil.rmtree(app_path)
                sys.exit()
            
            # copy tpl file to views/apps folder
            src = config.apps_dir + os.sep + app + os.sep + app + '.tpl'
            dst = 'views' + os.sep + 'apps'
            shutil.copy(src,dst)

            # add app to database
            appid = dal.db.apps.insert(name=app,
                               description=parsed['description'],
                               category=parsed['category'],
                               language=parsed['language'],
                               input_format=parsed['input_format'],
                               command=parsed['command'])
     
            # add plots and datasources to db
            if 'plots' in parsed.keys():
                for key in parsed['plots']:
                    pltid = dal.db.plots.insert(appid=appid, ptype=key['ptype'],
                                                title=key['title'], 
                                                options=key['options'])
                    for ds in key['datasource']:
                        dal.db.datasource.insert(pltid=pltid, 
                                                 filename=ds['filename'], 
                                                 cols=ds['cols'], 
                                                 line_range=ds['line_range'], 
                                                 data_def=ds['data_def'])
            # commit to db
            dal.db.commit()
            print "SUCCESS: installed app", app
        else:
            print install_usage

    elif (sys.argv[1] == "list"):
        list_usage = "usage: spc list [available|installed]"
        if (len(sys.argv) == 3):
            if (sys.argv[2] == "installed"):
                result = Apps.all()
                for r in result:
                    print r.name
            elif (sys.argv[2] == "available"):
                try:
                    response = urllib2.urlopen(url)
                    html = response.read()
                    root = ET.fromstring(html)
                    for child in root.findall("{http://s3.amazonaws.com/doc/2006-03-01/}Contents"):
                        for c in child.findall("{http://s3.amazonaws.com/doc/2006-03-01/}Key"):
                            (app,ext) = c.text.split(".")
                            print app 
                except:
                    print "ERROR: problem accessing network"
                    sys.exit()
            else:
                print list_usage
        else:
            print list_usage
    else:
        print "ERROR: option not supported"
        sys.exit()
