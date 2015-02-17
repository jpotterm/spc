#!/usr/bin/env python
import threading, time, os
import config
from multiprocessing import Process, BoundedSemaphore, Lock
from gluino import DAL, Field

#inspired from:
#http://taher-zadeh.com/a-simple-and-dirty-batch-job-scheduler-daemon-in-python/

class scheduler(object):
    """multi-process scheduler"""

    def __init__(self):
        self.sem = BoundedSemaphore(config.np) 
        self.mutex = Lock()
        # start polling thread which checks queue status every second
        t = threading.Thread(target = self.assignTask)
        t.start()

    def assignTask(self):
        while(True):
            #print "scheduler:", self.qstat(), "jobs in queued state", 
            #time.asctime()
            j = self.qfront()
            if j is not None and j > 0:
                self.start(j)            
            time.sleep(1) 

    def qsub(self,app,cid,user,np):
        """queue job ... really just set state to 'Q'."""
        state = 'Q'
        db = DAL(config.uri, auto_import=True, migrate=False, folder=config.dbdir)
        db.jobs.insert(user=user, app=app, cid=cid, state=state, 
                       time_submit=time.asctime(), np=np)
        db.commit()
        db.close()

    def qfront(self):
        """pop the top job off of the queue that is in a queued 'Q' state"""
        db = DAL(config.uri, auto_import=True, migrate=False, folder=config.dbdir)
        jid = db.jobs(db.jobs.state=='Q')
        db.close()
        if jid: return jid.id
        else: return None

    def qdel(self,jid):
        """delete job jid from the queue"""
        try:
            db = DAL(config.uri, auto_import=True, migrate=False, folder=config.dbdir)
            del db.jobs[jid]
            db.commit()
            db.close()
            return True
        except:
            return False
       

    def qstat(self):
        """return the number of jobs in a queued 'Q' state"""
        db = DAL(config.uri, auto_import=True, migrate=False, folder=config.dbdir)
        return db(db.jobs.state=='Q').count()
        db.close()

    def start(self,jid):
        """start running a job by creating a new process"""
        db = DAL(config.uri, auto_import=True, migrate=False, folder=config.dbdir)
        user = db.jobs(jid).user
        app = db.jobs(jid).app
        cid = db.jobs(jid).cid
        np = db.jobs(jid).np
        if np > 1: # use mpi
            command = db.apps(name=app).command
            command = config.mpirun + " -np " + str(np) + " " + command
        else: # dont use mpi
            command = db.apps(name=app).command

        exe = os.path.join(config.apps_dir,app,app)
        outfn = app + ".out"
        cmd = command + ' >& ' + outfn

        run_dir = os.path.join(config.user_dir,user,app,cid)

        # if number procs available fork new process with command
        for i in range(np):
            self.sem.acquire()
        p = Process(target=self.start_job, args=(run_dir,cmd,app,jid,np,))
        p.start()
        for i in range(np):
            self.sem.release()

    def start_job(self,run_dir,cmd,app,jid,np):
        """this is what the separate job process runs"""
        for i in range(np):
            self.sem.acquire()
        # update state to 'R' for run
        self.mutex.acquire()
        db = DAL(config.uri, auto_import=True, migrate=False, folder=config.dbdir)
        db.jobs[jid] = dict(state='R')
        db.commit()
        db.close()
        self.mutex.release()
        print 'start_job:',run_dir, cmd
        mycwd = os.getcwd()
        os.chdir(run_dir) # change to case directory
        os.system(cmd)
        # let user know job has ended
        outfn = app + ".out"
        with open(outfn,"a") as f:
            f.write("FINISHED EXECUTION")
        # update state to 'C' for completed
        os.chdir(mycwd) # return to SciPaaS root directory
        self.mutex.acquire()
        db = DAL(config.uri, auto_import=True, migrate=False, folder=config.dbdir)
        db.jobs[jid] = dict(state='C')
        db.commit()
        db.close()
        self.mutex.release()
        for i in range(np):
            self.sem.release()

    def stop(self,app):
        p.shutdown
        #os.system("killall " + app)