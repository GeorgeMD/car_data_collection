import subprocess
from subprocess import Popen, PIPE, STDOUT
import time
import os
import signal

from utils import get_nonblocking

CANDUMP_CMD = "candump -l"


def plog(s):
    print('[CAN] {}'.format(s))


def get_can(cfg):
    out_dir = cfg.out_dir
    queue = cfg.queue
    send_queue = cfg.send_queue
    receive_queue = cfg.receive_queue

    log_path = "{}/raw_can.log".format(out_dir)
    cmd = CANDUMP_CMD

    # Wait for start command:
    plog("Ready")
    receive_queue.put(True)
    resp = queue.get(block=True)
    if resp:
        plog("Start")
    else:
        return 1

    with open(log_path, "w") as outfile:
        pro = subprocess.Popen(cmd, stdout=PIPE, stderr=outfile, stdin=PIPE, bufsize=1, shell=True,
                               preexec_fn=os.setsid)

    # Wait for closing command
    while True:
        res = get_nonblocking(queue)
        time.sleep(1)
        if res:
            os.killpg(os.getpgid(pro.pid), signal.SIGTERM)
            # groups
            break

    return 0