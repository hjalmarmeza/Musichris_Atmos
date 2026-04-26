import os
import sys

acc_time = 1680
n_songs = 7

song_times = [
    ("Song 1", "Verse 1", 2, 12),
    ("Song 2", "Verse 2", 242, 252),
    ("Song 3", "Verse 3", 482, 492)
]
theme1 = "Paz"

font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
ff = f":fontfile='{font_path}'" if font_path else ""

def esc(t): return t.replace('\\','\\\\').replace("'","\\'").replace(':','\\:')

logo_path = "/home/runner/work/Musichris_Atmos/Musichris_Atmos/assets/Logo Hjalmar Animado.mp4"
logo_esc = logo_path.replace('\\', '/').replace("'", "\\'")

vf_parts = [
    "[0:v][1:v][2:v]concat=n=3:v=1:a=0[base_v]",
    f"movie=filename='{logo_esc}':loop=0,setpts=N/FRAME_RATE/TB,scale=120:-1,format=yuv420p[logo]",
    "[base_v][logo]overlay=x=40:y=40:shortest=1[v_logo]"
]

phrase = f"MÚSICA PARA {theme1.upper()}"
words = phrase.upper().split(' ')
mid = len(words) // 2
h1 = esc(' '.join(words[:mid]))
h2 = esc(' '.join(words[mid:]))

bx, by, bw, bh = "(W-900)/2", "(H-220)/2", 900, 220

vf_parts += [
    f"[v_logo]drawbox=x={bx}:y={by}:w={bw}:h={bh}:color=black@0.63:t=fill:enable='between(t,0,8)'[v_h1]",
    f"[v_h1]drawtext=text='{h1}'{ff}:fontsize=46:fontcolor=0xC5A059FF:x=(W-tw)/2:y=(H/2-60):enable='between(t,0,8)'[v_h2]",
    f"[v_h2]drawtext=text='{h2}'{ff}:fontsize=46:fontcolor=0xC5A059FF:x=(W-tw)/2:y=(H/2+10):enable='between(t,0,8)'[v_t1]"
]

curr_v = "[v_t1]"
for i, (title, verse, st, en) in enumerate(song_times):
    t = esc(title.upper()); v = esc(verse.upper())
    vf_parts += [
        f"{curr_v}drawbox=x=60:y=590:w=470:h=100:color=black@0.63:t=fill:enable='between(t,{st},{en})'[v_s{i}_1]",
        f"[v_s{i}_1]drawtext=text='{t}'{ff}:fontsize=32:fontcolor=0xC5A059FF:x=90:y=612:enable='between(t,{st},{en})'[v_s{i}_2]",
        f"[v_s{i}_2]drawtext=text='{v}'{ff}:fontsize=22:fontcolor=0xF5F5DCFF:x=90:y=652:enable='between(t,{st},{en})'[v_s{i}_3]"
    ]
    curr_v = f"[v_s{i}_3]"

os_t, os_e = int(acc_time - 8), int(acc_time)
vf_parts += [
    f"{curr_v}drawbox=x={bx}:y={by}:w={bw}:h={bh}:color=black@0.63:t=fill:enable='between(t,{os_t},{os_e})'[v_o1]",
    f"[v_o1]drawtext=text='CAMINEMOS JUNTOS EN FE'{ff}:fontsize=44:fontcolor=0xC5A059FF:x=(W-tw)/2:y=(H/2-60):enable='between(t,{os_t},{os_e})'[v_o2]",
    f"[v_o2]drawtext=text='SUSCRÍBETE @MUSICHRIS_STUDIO'{ff}:fontsize=32:fontcolor=0xF5F5DCFF:x=(W-tw)/2:y=(H/2+10):enable='between(t,{os_t},{os_e})'[v_o3]",
    f"[v_o3]fade=t=in:st=0:d=2,fade=t=out:st={int(acc_time)-2}:d=2[v_out]"
]

vf_chain = ";".join(vf_parts)

af_parts = []
for i in range(n_songs):
    af_parts.append(f"[{i+3}:a]aresample=44100,settb=AVTB[as{i}]")

a_tags = "".join([f"[as{i}]" for i in range(n_songs)])
af = ";".join(af_parts) + f";{a_tags}concat=n={n_songs}:v=0:a=1,afade=t=in:st=0:d=2,afade=t=out:st={int(acc_time)-2}:d=2[a_out]"

print(f"{vf_chain};{af}")
