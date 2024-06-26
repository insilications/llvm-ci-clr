#!/usr/bin/python3
import subprocess
import os
import sys
import re


def dump_bc(base, dis, count, data):
    filename = "{}/seg{}.bc".format(base, count)
    with open(filename, "wb") as f:
        f.write(data)
    subprocess.run([dis, "seg{}.bc".format(count)], cwd=base)


def extract_bc(filename: str, objcopy, dis):
    bc_header = bytes([0x42, 0x43, 0xc0, 0xde])
    basedir = filename+"_bc"
    bc_filename = filename+".bc"

    subprocess.run([objcopy, filename, "--dump-section",
                   ".llvmbc={}".format(bc_filename)])

    if not os.path.exists(bc_filename):
        return

    os.makedirs(basedir, exist_ok=True)

    count = 0

    with open(bc_filename, 'rb') as f:
        data = f.read()

        last_pos = 0
        while True:
            pos = data.find(bc_header, last_pos+4)
            if pos == -1:
                dump_bc(basedir, dis, count, data[last_pos:])
                break
            else:
                dump_bc(basedir, dis, count, data[last_pos: pos])
            last_pos = pos
            count += 1


def check_access(bin):
    return os.path.exists(bin) and os.access(bin, os.X_OK)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: binutils.py <llvm-bin-path> binary1')
        exit(1)

    llvm_path = os.path.abspath(sys.argv[1]).removesuffix('/')
    llvm_dis = llvm_path + '/llvm-dis'
    llvm_objdump = llvm_path + "/llvm-objdump"
    llvm_objcopy = llvm_path + "/llvm-objcopy"
    # llvm_diff = llvm_path + "/llvm-diff"

    # if not (check_access(llvm_dis) and check_access(llvm_objdump) and check_access(llvm_objcopy) and check_access(llvm_diff)):
    if not (check_access(llvm_dis) and check_access(llvm_objdump) and check_access(llvm_objcopy)):
        print('Error: invalid llvm binaries path')
        exit(1)


    extract_bc(sys.argv[2], llvm_objcopy, llvm_dis)

    # diff_ir("irdiff", sys.argv[2]+"_bc", sys.argv[3]+"_bc", llvm_diff)
