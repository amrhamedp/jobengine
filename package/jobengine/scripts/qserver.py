#!/usr/bin/env python

import time
# sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine 
# jobengire
from jobengine.core import Job, test_workdir
from jobengine.clusters import Clusters
from jobengine.configuration import engine_file

import argparse
import subprocess

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--action", default="resubmit")
    return parser.parse_args()

def process_resubmit():

    engine = create_engine(engine_file)
    Session = sessionmaker(bind=engine)
    session = Session()
    clusters = Clusters()
    
    while True:
        print("Checking")
        jobs = [job for job in session.query(Job).order_by(Job.id)]
        for job in jobs :
            cluster, shell = clusters.get_cluster(job.cluster_name)
            if job.status == "S": continue
            status = cluster.get_status(shell, job)
            job.status = status 
            print("Before:",status, job.id)
            if status == "C":
                job = cluster.submit(shell, job)
                print("After:", job.status, job.id)
            session.add(job)
            session.commit()
        break
        time.sleep(5*60) # 5 minutes

def process_fetch():

    engine = create_engine(engine_file)
    Session = sessionmaker(bind=engine)
    session = Session()
    clusters = Clusters()
    
    while True:
        print("Checking")
        jobs = [job for job in session.query(Job).order_by(Job.id)]
        cluster, shell = clusters.get_cluster(job.cluster_name)
        for job in jobs :
            print(cluster.pull(shell, job))   
            print(job.status, job.id, job.workdir)
        break
        #time.sleep(60*60) # 60 minutes

def process_test():
    
    engine = create_engine(engine_file)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    while True:
        print("Testing")
        jobs = [job for job in session.query(Job).order_by(Job.id)]
        for job in jobs :
            print job.local_workdir, test_workdir(job.workdir)
        break
        #time.sleep(60*60) # 60 minutes

from multiprocessing import Process    

def main():
    args = parse_args()
  
    if args.action == "resubmit":
        process_resubmit()
    if args.action == "fetch":
        process_fetch()
    if args.action == "test":
        process_test()
    #Process(target=process_resubmit).start()
    #Process(target=process_fetch).start()    
    
if __name__ == '__main__':
    main()    
