import customtkinter as ctk
from customtkinter import filedialog
from tkinter import messagebox
from PIL import Image
import numpy,subprocess,os,sys,ctypes

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad
from Crypto.Util.Padding import unpad

#for admin stuff

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    params = " ".join([f'"{arg}"' for arg in sys.argv[1:]])
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, f'"{sys.argv[0]}" {params}', None, 1
    )
    sys.exit()

if not is_admin():
    run_as_admin()

#GUI
def unfocus(event):
    widget = event.widget
    if str(widget)not in [".!ctktabview.!ctkframe.!ctkframe2.!ctkentry.!entry",".!ctktabview.!ctkframe2.!ctkframe2.!ctkentry.!entry",".!ctktabview.!ctkframe2.!ctkframe3.!ctkentry2.!entry"]:
        window.focus_set()
encrypt_mode="XOR"
def set_encrypt_mode(new_mode):
    global encrypt_mode
    encrypt_mode=new_mode
    if new_mode=="XOR":
        key_entry.configure(state="normal")
        key_entry.configure(placeholder_text="ENCRYPTION KEY🔑")
    if new_mode=="AES":
        key_entry.configure(placeholder_text="AESMODE-CANNOT SET KEY")
        key_entry.configure(state="disabled")
decrypt_mode="XOR"
def set_decrypt_mode(new_mode):
    global decrypt_mode
    decrypt_mode=new_mode
    if new_mode=="XOR":
        decrypt_key_entry.configure(placeholder_text="DECRYPTION KEY🔑")
    if new_mode=="AES":
        decrypt_key_entry.configure(placeholder_text="<KEY>-<IV>")
def resource_path(relative_path): #util
    try:
        base_path = sys._MEIPASS 
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
mp4edit = resource_path(os.path.join("dependencies", "Bento4", "bin", "mp4edit.exe"))

def openFileDialog(entry,filetype_tuple=None,type=True):
    file_path=filedialog.askopenfilename(
        title="Select File",
        filetypes=(filetype_tuple ,) if filetype_tuple else (('All Files','*.*'),)
    ) if type else filedialog.askdirectory(
        title="Where to save encrypted file?"
    )
    if file_path:
        entry.state="normal"
        entry.delete(0,ctk.END)
        entry.insert(0,file_path)

def prepare_for_encryption(key_entry,secret_entry,host_entry,output_entry):
    key=key_entry.get()
    secret_path=secret_entry.get()
    host_path=host_entry.get()
    output_path=output_entry.get()
    if not key and encrypt_mode=="XOR":
        messagebox.showerror("Encryption: Missing key",'Please enter encryption key! (The longer the better)')
        return
    for thing in [secret_path,host_path,output_path]:
        if thing.startswith('Select'):
            messagebox.showerror("Encryption: Missing file DIR",'Please '+thing)
            return
    try:
        hide_secret(key,secret_path,host_path,os.path.join(output_path,'output.mp4'))
    except Exception as e:
        messagebox.showerror("Encryption:error",e)
    
    # hide_secret(key,secret_path,host_path,os.path.join(output_path,'output.mp4'))
    # messagebox.showinfo("Encryption: Success!",f"Encrypted file (output.mp4) created at {output_path}")       

def prepare_for_decryption(key_entry,encrypted_entry,output_entry,extension_entry):
    key=key_entry.get()
    encrypted_path=encrypted_entry.get()
    output_path=output_entry.get()
    extension=extension_entry.get()
    if not extension.startswith('.') and len(extension)>0:
        extension='.'+extension
    if not key:
        messagebox.showerror("Decrypt: Missing key","Please enter a decryption key!")
        return
    for thing in [encrypted_path,output_path]:
        if thing.startswith("Select"):
            messagebox.showerror("Decrypt: Missing file DIR","Please "+thing)
            return
    try:
           reveal_secret(key,encrypted_path,os.path.join(output_path,"decrypted"+extension))
    except Exception as e:
          messagebox.showerror("Decryption: error",e)
          return
    messagebox.showinfo("Decryption: Success!",f"Decrypted file (decrypted{extension}) created at {output_path}")       
    
    
        
    
def toggle_password(show_button,key_entry):
    key_entry.configure(show='' if key_entry.cget('show')=='*' else '*')
    show_button.configure(text='⌣' if key_entry.cget('show')=='*' else '👁')
#backend

def xor_cipher(key,secret):
    key=key.encode('utf-8')
    key_len=len(key)
    encrypted_secret=bytearray()
    for i,b in enumerate(secret):
        encrypted_secret.append(b^key[i%key_len])
    return encrypted_secret
def aes_cipher(secret):
    key = get_random_bytes(16)
    iv = get_random_bytes(16)
    cipher=AES.new(key,AES.MODE_CBC,iv)
    ciphertext=cipher.encrypt(pad(secret,AES.block_size))
    return ciphertext,key,iv
def hide_secret(key,secret_path,host_path,output_path):
    secret=open(secret_path,'rb').read()
    if encrypt_mode=="XOR":
        encrypted_secret=xor_cipher(key,secret)
    if encrypt_mode=="AES":
        encrypted_secret,key,iv=aes_cipher(secret)
        with open(f"{os.path.join(output_path[0:-10],'credentials.txt')}",'w') as f:
            f.write(key.hex())
            f.write('-')
            f.write(iv.hex())
        messagebox.showinfo("Encryption: ",f"AES <key>-<id> created at {output_path[0:-10]}\nPlease don't lose this file!!")
        
            
            
        
    temp_name=''.join(chr(x) for x in numpy.random.randint(97,123,10))
        
    
    atom_size=8+len(encrypted_secret)
    atom_size=atom_size.to_bytes(4,'big')
    atom_type=b'free'
    
    # current_path=os.path.dirname(os.path.abspath(__file__))
    free_cleaner(path=host_path)
    
    with open(temp_name+'.atom','wb') as f:
        f.write(atom_size)
        f.write(atom_type)
        f.write(encrypted_secret)
    try:
        subprocess.run(f'{mp4edit} --insert moov:{temp_name}.atom:0 "{host_path}" "{output_path}"',check=True)
    except Exception as e:
          messagebox.showerror("Encryption: error",e)
          os.remove(temp_name+'.atom')
          return
    os.remove(temp_name+'.atom') 
    messagebox.showinfo("Encryption: Success!",f"Encrypted file (output.mp4) created at {output_path}")       
    return True

def free_cleaner(path):
    directory=os.path.split(path)[0]
    temp_name = ''.join(chr(x) for x in numpy.random.randint(97,123,10))
    tmp = os.path.join(directory, temp_name + ".tmp")
    print(tmp,path)
    cmd=f'{mp4edit} --remove free "{path}" "{tmp}" '
    check=subprocess.run(cmd,capture_output=True)
    if check.stderr:
        os.remove(tmp)
    else:
        messagebox.showwarning("Wild free atom!","Video has an unknown free atom\nOverwriting...")
        os.replace(tmp,path)
            
    
def free_hunter(data, start, end):
    i = start
    while i + 8 <= end:
        atom_size = int.from_bytes(data[i:i+4], "big")
        atom_type = data[i+4:i+8]
        if atom_size == 0:
            atom_size = end - i
        if atom_type == b"free":
            return data[i+8:i+atom_size]
        if atom_type == b"moov":
            found = free_hunter(data, i+8, i+atom_size)
            if found:
                return found
        i += atom_size
    return None

    
def xor_decipher(key,encrypted):
    key=key.encode('utf-8')
    key_len=len(key)
    decrypted_data=bytearray()
    for i,b in enumerate(encrypted):
        decrypted_data.append(b^key[i%key_len])
    return decrypted_data
def aes_decipher(key_iv,encrypted):
    key,iv=key_iv.split('-')
    key=bytes.fromhex(key)
    iv=bytes.fromhex(iv)
    
    cipher=AES.new(key,AES.MODE_CBC,iv)
    decrypted_bin=unpad(cipher.decrypt(encrypted),AES.block_size)
    return decrypted_bin
def reveal_secret(key,host_path,output_path):
    host=open(host_path,'rb').read()
    encrypted_data=free_hunter(host,0,len(host))
    
    if decrypt_mode=="XOR":
        decrypted_data=xor_decipher(key,encrypted_data)
    if decrypt_mode=="AES":
        decrypted_data=aes_decipher(key,encrypted_data)
    
    open(output_path,'wb').write(decrypted_data)
  


ctk.set_widget_scaling(1.5)

window=ctk.CTk()
window.title('Atom Appender :))')
window.bind('<Button-1>',unfocus)

# mp4edit = resource_path(os.path.join("dependencies", "Bento4", "bin", "mp4edit.exe"))
# print(mp4edit)


tabs=ctk.CTkTabview(window,fg_color="silver")
tabs.pack(expand=True,fill='both')


encrypt_tab=tabs.add('Encrypt')
decrypt_tab=tabs.add('Decrypt')
about_tab=tabs.add('About')

encrypt_tab.grid_rowconfigure((0,1,2),weight=1)
encrypt_tab.grid_columnconfigure(0,weight=1)
encrypt_row=[]
encrypt_row_count=3
for i in range(encrypt_row_count):
    row_e=ctk.CTkFrame(encrypt_tab,fg_color='transparent')
    row_e.grid(row=i,column=0)
    encrypt_row.append(row_e)

mp4_entry=ctk.CTkEntry(encrypt_row[0])    
mp4_entry.insert(0,"Select MP4 File")
mp4_entry.state="disabled"
mp4_entry.pack(side='left',padx=0)


select_mp4=ctk.CTkButton(encrypt_row[0],text="📁",width=10,fg_color='#ebcc34',text_color='black',command=lambda:openFileDialog(mp4_entry,filetype_tuple=('MP4 Files','*.mp4')))
select_mp4.pack(side='left',padx=(0,10),pady=10)

secret_entry=ctk.CTkEntry(encrypt_row[0])    
secret_entry.insert(0,"Select secret File")
secret_entry.state="disabled"
secret_entry.pack(side='left',padx=0)

select_secret=ctk.CTkButton(encrypt_row[0],text="📁",width=10,fg_color='#ebcc34',text_color='black',command=lambda:openFileDialog(secret_entry))
select_secret.pack(side='left',padx=5,pady=10)


key_entry=ctk.CTkEntry(encrypt_row[1],placeholder_text="ENCRYPTION KEY🔑")
key_entry.pack(side='left',expand=True,fill='x',padx=20,pady=10)

encryption_method_combobox=ctk.CTkComboBox(encrypt_row[1],values=["XOR","AES"],command=set_encrypt_mode)
encryption_method_combobox.pack(pady=(10,0))
# ctk.CTkLabel(encrypt_row[1],text="Encryption Method: XOR (More coming soon)",text_color='white',fg_color='grey',corner_radius=10).pack(side='left')



output_entry=ctk.CTkEntry(encrypt_row[2])    
output_entry.insert(0,"Select output directory")
output_entry.state="disabled"
output_entry.pack(side='left',padx=0)

select_output=ctk.CTkButton(encrypt_row[2],text="📁",width=10,fg_color='#ebcc34',text_color='black',command=lambda:openFileDialog(output_entry,type=False))
select_output.pack(side='left',pady=10)

encrypt_button=ctk.CTkButton(encrypt_row[2],text="Encrypt!",command=lambda:prepare_for_encryption(key_entry,secret_entry,mp4_entry,output_entry))
encrypt_button.pack(side="left",padx=10)


decrypt_tab.grid_rowconfigure((0,1,2),weight=1)
decrypt_tab.grid_columnconfigure(0,weight=1)

decrypt_row=[]
decrypt_row_count=3
for i in range(decrypt_row_count):
    row_d=ctk.CTkFrame(decrypt_tab,fg_color='transparent')
    row_d.grid(row=i,column=0)
    decrypt_row.append(row_d)
    
decrypt_entry=ctk.CTkEntry(decrypt_row[0])    
decrypt_entry.insert(0,"Select encrypted MP4")
decrypt_entry.state="disabled"
decrypt_entry.pack(side='left',padx=0)

    
select_decrypt=ctk.CTkButton(decrypt_row[0],text="📁",width=10,fg_color='#ebcc34',text_color='black',command=lambda:openFileDialog(decrypt_entry,('MP4 Files',"*.mp4"),type=True))
select_decrypt.pack(side='left')

decrypt_key_entry=ctk.CTkEntry(decrypt_row[1],placeholder_text="DECRYPTION KEY🔑",show='*')
decrypt_key_entry.pack(side='left',expand=True,fill='x',pady=10)

show_pass_button=ctk.CTkButton(decrypt_row[1],text="⌣",width=10,anchor='center',command=lambda:toggle_password(show_pass_button,decrypt_key_entry))
show_pass_button.pack(side="left",padx=(0,10))

# ctk.CTkLabel(decrypt_row[1],text="Encryption Method: XOR (More coming soon)",text_color='white',fg_color='grey',corner_radius=10).pack(side='left')
decryption_method_combobox=ctk.CTkComboBox(decrypt_row[1],values=["XOR","AES"],command=set_decrypt_mode)
decryption_method_combobox.pack(pady=(10,0))


decrypt_output_entry=ctk.CTkEntry(decrypt_row[2])    
decrypt_output_entry.insert(0,"Select path to save decrypted file")
decrypt_output_entry.state="disabled"
decrypt_output_entry.pack(side='left',padx=0)

    
select_decrypt_output=ctk.CTkButton(decrypt_row[2],text="📁",width=10,fg_color='#ebcc34',text_color='black',command=lambda:openFileDialog(decrypt_output_entry,type=False))
select_decrypt_output.pack(side='left')

decrypt_extention_entry=ctk.CTkEntry(decrypt_row[2],placeholder_text=".file_extention(optional)")
decrypt_extention_entry.pack(side='left')

decrypt_button=ctk.CTkButton(decrypt_row[2],text="Decrypt!",command=lambda:prepare_for_decryption(decrypt_key_entry,decrypt_entry,decrypt_output_entry,decrypt_extention_entry))
decrypt_button.pack()

about_tab.grid_columnconfigure((0,1),weight=1)
about_tab.grid_rowconfigure(0,weight=1)
about_column=[]
for i in range(2):
    column=ctk.CTkFrame(about_tab,fg_color='transparent')
    column.grid(row=0,column=i)
    about_column.append(column)

ctk.CTkLabel(about_column[0],text="Hide up to 4GB of data ANY type inside of ANY mp4",text_color='black',fg_color="white",corner_radius=10).pack(side='top',padx=10,pady=5)
ctk.CTkLabel(about_column[0],text="Made by Duy Nguyen \n For College project \nDev Notes\n -7h43PM 4/10/2025 Encryption Worked!(-v1.0Alpha)\n-9h40PM 4/10/2025 decryption worked! I'm so sleepy asdadwawsd (-v1.0Beta)\n 12h25AM 5/10 fix bugs to plugnplay mp4edit (-v1.1Beta) \n3:13PM 23/10/2025 adding AES (v2.0alpha)\n5:11PM 23/10/2025 NEW AES feature(v2.0beta)\n3:17PM 25/10/2025 Bug Fix: Clean wild free atoms before encryption!(v2.1beta) \n\n v2.1Beta",text_color='black',fg_color="white",corner_radius=10).pack(side='bottom',padx=10,pady=5)

try:
    current_path=os.path.dirname(os.path.abspath(__file__))
    my_pic=Image.open(os.path.join(current_path,'dependencies','img','me.jpg'))
    my_ctk_pic=ctk.CTkImage(light_image=my_pic,dark_image=my_pic,size=(150,200))
    about_pic=ctk.CTkLabel(about_column[1],image=my_ctk_pic,text="HI:)", text_color='white')
    about_pic.pack()
except Exception:
    about_pic=ctk.CTkLabel(about_column[1],text="PICTURE OF ME, FILE NOT FOUND :(", text_color='red')
    about_pic.pack()
window.mainloop()

