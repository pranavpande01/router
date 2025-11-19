def hit(input:str,output:str):
    import os 
    command=f"""
    mineru -p "{input}" \
    -o {output} \
    -b vlm-http-client \
    -u http://localhost:30000
    """
    os.system(command)

#print(hit("/home/ubuntu/pranav/titan_archive/MB25P291/main/MB25P291.pdf","/home/ubuntu/pranav/titan_archive/output"))