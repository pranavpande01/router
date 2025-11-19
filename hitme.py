def hit(input:str,output:str):
    import os 
    command=f"""
    mineru -p "{input}" \
    -o {output} \
    -b vlm-http-client \
    -u http://localhost:30000
    """
    os.system(command)

