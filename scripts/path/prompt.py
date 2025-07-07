
import sys

def main():
    if len(sys.argv) != 4:
        print("Usage: python3 gen_prompt.py FUNC1 FUNC2 DRIVER")
        exit(1)

    FUNC1 = sys.argv[1]
    FUNC2 = sys.argv[2]
    DRIVER = sys.argv[3]

    template = """
You are an expert of linux-6.12-rc7 kernel drivers/, I am working on the data race on it.
I am working on triggering two specific lines to trigger a data race bug in linux kernel driver. Your task is to find the correct way to trigger them from a user-space C program using ioctl/system call.

## Details steps
What you should do can be summriazed into four steps: (1)Understand the logic of the code (3)Find the ioctl that will trigger the two function (3)Find the ioctl that will trigger the two function (4)Find the reasonalbe value of the argument (5)Generate a C program to trigger it

### (1)Understand the logic of the code
0. I am working on a function pair, the {FUNC1} and {FUNC2} in the driver "{DRIVER}".
1. I have given you the source code in the attachment in the format of the json named {FUNC1}-{FUNC2}.json In this file, you can see two parts, each one for the two functions. And in each part, there are several small paths, they are the call chains in the {DRIVER}/, from the top function (usually the ioctl handler or trigger), to the other functions until the two function I want to trigger. In each path, there are several points, each one is a function which is a point the path need to go through, start from the beginning of the point function to the caller to the next function in the path. And the last line of the last point in each path is the line in the {FUNC1} and {FUNC2} we want to trigger.
2. You need to understand the logic of the code according to these information I gave, if you need the defination during the path, you can search on the internet of the linux kernel-6.12-rc7.
3. After you understand the logic of the code, you should analyze it why it can lead to a data race, so that you can make use of this point later when you generate the C program.

### (2)Find the ioctl that will trigger the two function
1. It is easy for you to find out the ioctl/syscall that can trigger the function of {FUNC1} {FUNC2} in the driver "{DRIVER}".
2. In the attachment .txt and .txt.const file, I gave you the def of all the ioctl in the {DRIVER} and the const defined in the {DRIVER}, you should make full use of them.

### (3)Summarize the context
0. After you find the ioctl that will trigger the {FUNC1} {FUNC2}, you should summarize the context.
1. The context in this context is the dependencies need to be satisfied or the state need to be set before I call the ioctl that can trigger the specific line, like some special state requirments, other ioctl need to be called......

### (4)Find the reasonalbe value of the argument
0. After we get the context, the last thing is to find the reasonable of the argument value.
1. You need to set an reasonable value of the argument struct, you should check both the .txt, .txt.const and the {FUNC1}-{FUNC2}.json I gave you to understand the struct item in the argument struct, and set a reasonable value to it, like for a mem address, you should set a value like address but not 15 or what ever, and also for a user space mem address, set a valid address for the user but not a system one.
2. During this step, you should make full use of the context you summriaze in the last step, so that you can set it more efficient and efficitive.

### (5)Generate C programs to trigger the two line
0. Check the step (1)-(4) you did just now to find if there is somewhere confusing or wrong and fix them.
1. After you get all the steps before done, you can genereate a lot of C programs to trigger the two lines now, one program for one function, and using different path I gave you.
2. About the device, I have uploaded all the device on the qemu for you to use, you can find the one you think is the correct device in the attachment dev.list
3. Remember to set the include file and the def file that needed by the program. 

## Remark
1. If you have and problems, just ask me.
2. Please write everything in main for each program, trigger two lines.
3. Please just write C programs to trigger these two lines, no need to set a thread process to run them both, I will do it later. No need to set the window,And the line I want to trigger is the last line of the last function in each path.
4. In each program the ioctl you want to use, you need to def before you use them.
5. Speak In Englishdans
"""

    
    output = template.format(FUNC1=FUNC1, FUNC2=FUNC2, DRIVER=DRIVER)

  
    filename = f"{FUNC1}-{FUNC2}.prompt"


    with open(filename, "w") as f:
        f.write(output)

    # print(f"Prompt generated and written to {filename}")

if __name__ == "__main__":
    main()