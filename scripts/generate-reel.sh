#!/bin/bash
# Generate a futuristic Instagram Reel for Scan - Peptide AI App
# Output: 1080x1920 (9:16), 15 seconds, MP4

set -e

OUT="/home/user/Ad-Videos/output"
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_LIGHT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
GREEN="0x00E676"
DARK_GREEN="0x00C853"
BG="0x0A0A0A"
W=1080
H=1920
FPS=30

mkdir -p "$OUT/scenes"

# ══════════════════════════════════════════════════════════════════════════════
# SCENE 1: Opening — DNA helix particles + "SCAN" reveal (0-3s)
# ══════════════════════════════════════════════════════════════════════════════
echo "Generating Scene 1: Opening..."
ffmpeg -y -f lavfi -i "color=c=0x0A0A0A:s=${W}x${H}:d=3:r=${FPS}" \
  -vf "
    drawtext=fontfile=${FONT}:text='S C A N':fontcolor=0x00E676:fontsize=120:
      x=(w-text_w)/2:y=(h-text_h)/2-100:
      alpha='if(lt(t,0.5),0,if(lt(t,1.5),min((t-0.5)*2\,1),1))',
    drawtext=fontfile=${FONT_LIGHT}:text='Peptide Intelligence':fontcolor=0x00E676@0.7:fontsize=42:
      x=(w-text_w)/2:y=(h/2)+40:
      alpha='if(lt(t,1),0,if(lt(t,2),min((t-1)*2\,1),1))',
    drawtext=fontfile=${FONT_LIGHT}:text='━━━━━━━━━━━━━━━━':fontcolor=0x00E676@0.3:fontsize=36:
      x=(w-text_w)/2:y=(h/2)+120:
      alpha='if(lt(t,1.5),0,if(lt(t,2.5),(t-1.5)*2,1))',
    drawtext=fontfile=${FONT_LIGHT}:text='◆':fontcolor=0x00E676@0.5:fontsize=200:
      x='(w-text_w)/2+sin(t*3)*50':y='h/2-400+cos(t*2)*30':
      alpha='if(lt(t,0.3),t/0.3,0.4)',
    drawtext=fontfile=${FONT_LIGHT}:text='◇':fontcolor=0x00E676@0.3:fontsize=150:
      x='w*0.2+sin(t*2+1)*40':y='h*0.15+cos(t*3)*20':
      alpha='0.3',
    drawtext=fontfile=${FONT_LIGHT}:text='◇':fontcolor=0x00E676@0.3:fontsize=100:
      x='w*0.75+sin(t*2.5)*30':y='h*0.8+cos(t*1.5)*25':
      alpha='0.25'
  " \
  -c:v libx264 -pix_fmt yuv420p "$OUT/scenes/scene1.mp4"

# ══════════════════════════════════════════════════════════════════════════════
# SCENE 2: Problem Statement — "Your peptides. Optimized by AI." (3-6s)
# ══════════════════════════════════════════════════════════════════════════════
echo "Generating Scene 2: Problem statement..."
ffmpeg -y -f lavfi -i "color=c=0x0A0A0A:s=${W}x${H}:d=3:r=${FPS}" \
  -vf "
    drawbox=x=0:y=0:w=iw:h=4:color=0x00E676@0.8:t=fill,
    drawbox=x=0:y=ih-4:w=iw:h=4:color=0x00E676@0.8:t=fill,
    drawtext=fontfile=${FONT}:text='Your peptides.':fontcolor=white:fontsize=72:
      x=(w-text_w)/2:y=h/2-200:
      alpha='if(lt(t,0.3),0,min((t-0.3)*3\,1))',
    drawtext=fontfile=${FONT}:text='Optimized':fontcolor=0x00E676:fontsize=90:
      x=(w-text_w)/2:y=h/2-60:
      alpha='if(lt(t,0.8),0,min((t-0.8)*3\,1))',
    drawtext=fontfile=${FONT}:text='by AI.':fontcolor=white:fontsize=72:
      x=(w-text_w)/2:y=h/2+80:
      alpha='if(lt(t,1.3),0,min((t-1.3)*3\,1))',
    drawbox=x='w/2-150':y='h/2+200':w=300:h=3:color=0x00E676@0.6:t=fill,
    drawtext=fontfile=${FONT_LIGHT}:text='BPC-157  ·  Semax  ·  GHK-Cu':fontcolor=0x00E676@0.5:fontsize=32:
      x=(w-text_w)/2:y=h/2+240:
      alpha='if(lt(t,1.8),0,min((t-1.8)*2\,1))'
  " \
  -c:v libx264 -pix_fmt yuv420p "$OUT/scenes/scene2.mp4"

# ══════════════════════════════════════════════════════════════════════════════
# SCENE 3: Feature — Body Scan (6-9s)
# ══════════════════════════════════════════════════════════════════════════════
echo "Generating Scene 3: Body Scan feature..."
ffmpeg -y -f lavfi -i "color=c=0x0A0A0A:s=${W}x${H}:d=3:r=${FPS}" \
  -vf "
    drawbox=x='w/2-200':y='h/2-350':w=400:h=500:color=0x00E676@0.15:t=fill,
    drawbox=x='w/2-200':y='h/2-350':w=400:h=500:color=0x00E676@0.6:t=3,
    drawbox=x='w/2-180':y='h/2-350+t*200':w=360:h=3:color=0x00E676@0.8:t=fill,
    drawtext=fontfile=${FONT}:text='BODY SCAN':fontcolor=0x00E676:fontsize=64:
      x=(w-text_w)/2:y=h/2-280:
      alpha='if(lt(t,0.3),0,min((t-0.3)*3\,1))',
    drawtext=fontfile=${FONT_LIGHT}:text='AI-powered biomarker':fontcolor=white@0.8:fontsize=36:
      x=(w-text_w)/2:y=h/2-180:
      alpha='if(lt(t,0.6),0,min((t-0.6)*3\,1))',
    drawtext=fontfile=${FONT_LIGHT}:text='analysis in real-time':fontcolor=white@0.8:fontsize=36:
      x=(w-text_w)/2:y=h/2-130:
      alpha='if(lt(t,0.6),0,min((t-0.6)*3\,1))',
    drawtext=fontfile=${FONT}:text='ACTIVE':fontcolor=0x00E676@0.7:fontsize=28:
      x=w/2-170:y=h/2+10:alpha='if(lt(t,1),0,min((t-1)*3\,1))',
    drawtext=fontfile=${FONT}:text='3':fontcolor=white:fontsize=56:
      x=w/2-160:y=h/2+50:alpha='if(lt(t,1.1),0,min((t-1.1)*3\,1))',
    drawtext=fontfile=${FONT}:text='LOGGED':fontcolor=0x00E676@0.7:fontsize=28:
      x=w/2-40:y=h/2+10:alpha='if(lt(t,1.2),0,min((t-1.2)*3\,1))',
    drawtext=fontfile=${FONT}:text='3':fontcolor=white:fontsize=56:
      x=w/2-25:y=h/2+50:alpha='if(lt(t,1.3),0,min((t-1.3)*3\,1))',
    drawtext=fontfile=${FONT}:text='STREAK':fontcolor=0x00E676@0.7:fontsize=28:
      x=w/2+90:y=h/2+10:alpha='if(lt(t,1.4),0,min((t-1.4)*3\,1))',
    drawtext=fontfile=${FONT}:text='3':fontcolor=white:fontsize=56:
      x=w/2+110:y=h/2+50:alpha='if(lt(t,1.5),0,min((t-1.5)*3\,1))'
  " \
  -c:v libx264 -pix_fmt yuv420p "$OUT/scenes/scene3.mp4"

# ══════════════════════════════════════════════════════════════════════════════
# SCENE 4: Stack Feature (9-12s)
# ══════════════════════════════════════════════════════════════════════════════
echo "Generating Scene 4: Stack feature..."
ffmpeg -y -f lavfi -i "color=c=0x0A0A0A:s=${W}x${H}:d=3:r=${FPS}" \
  -vf "
    drawtext=fontfile=${FONT}:text='TODAYS STACK':fontcolor=0x00E676:fontsize=56:
      x=(w-text_w)/2:y=h/2-300:
      alpha='if(lt(t,0.2),0,min((t-0.2)*4\,1))',
    drawbox=x='w/2-220':y='h/2-200':w=440:h=100:color=0x1A1A1A:t=fill,
    drawbox=x='w/2-220':y='h/2-200':w=440:h=100:color=0x00E676@0.4:t=2,
    drawtext=fontfile=${FONT}:text='BPC-157':fontcolor=white:fontsize=40:
      x=w/2-190:y=h/2-180:alpha='if(lt(t,0.5),0,min((t-0.5)*4\,1))',
    drawtext=fontfile=${FONT_LIGHT}:text='250mcg · SubQ · 08\\:00 AM':fontcolor=white@0.5:fontsize=26:
      x=w/2-190:y=h/2-130:alpha='if(lt(t,0.6),0,min((t-0.6)*4\,1))',
    drawbox=x='w/2-220':y='h/2-70':w=440:h=100:color=0x1A1A1A:t=fill,
    drawbox=x='w/2-220':y='h/2-70':w=440:h=100:color=0x00E676@0.4:t=2,
    drawtext=fontfile=${FONT}:text='Semax':fontcolor=white:fontsize=40:
      x=w/2-190:y=h/2-50:alpha='if(lt(t,0.8),0,min((t-0.8)*4\,1))',
    drawtext=fontfile=${FONT_LIGHT}:text='300mcg · Nasal · 12\\:00 PM':fontcolor=white@0.5:fontsize=26:
      x=w/2-190:y=h/2+0:alpha='if(lt(t,0.9),0,min((t-0.9)*4\,1))',
    drawbox=x='w/2-220':y='h/2+60':w=440:h=100:color=0x1A1A1A:t=fill,
    drawbox=x='w/2-220':y='h/2+60':w=440:h=100:color=0x00E676@0.4:t=2,
    drawtext=fontfile=${FONT}:text='GHK-Cu':fontcolor=white:fontsize=40:
      x=w/2-190:y=h/2+80:alpha='if(lt(t,1.1),0,min((t-1.1)*4\,1))',
    drawtext=fontfile=${FONT_LIGHT}:text='200mcg · SubQ · 06\\:00 PM':fontcolor=white@0.5:fontsize=26:
      x=w/2-190:y=h/2+130:alpha='if(lt(t,1.2),0,min((t-1.2)*4\,1))',
    drawtext=fontfile=${FONT_LIGHT}:text='AI-optimized dosing & timing':fontcolor=0x00E676@0.6:fontsize=32:
      x=(w-text_w)/2:y=h/2+230:alpha='if(lt(t,1.8),0,min((t-1.8)*3\,1))'
  " \
  -c:v libx264 -pix_fmt yuv420p "$OUT/scenes/scene4.mp4"

# ══════════════════════════════════════════════════════════════════════════════
# SCENE 5: CTA — Download / Coming Soon (12-15s)
# ══════════════════════════════════════════════════════════════════════════════
echo "Generating Scene 5: CTA..."
ffmpeg -y -f lavfi -i "color=c=0x0A0A0A:s=${W}x${H}:d=3:r=${FPS}" \
  -vf "
    drawtext=fontfile=${FONT}:text='S C A N':fontcolor=0x00E676:fontsize=100:
      x=(w-text_w)/2:y=h/2-250:
      alpha='if(lt(t,0.3),0,min((t-0.3)*3\,1))',
    drawbox=x='w/2-150':y='h/2-120':w=300:h=3:color=0x00E676@0.5:t=fill,
    drawtext=fontfile=${FONT_LIGHT}:text='The future of':fontcolor=white@0.8:fontsize=44:
      x=(w-text_w)/2:y=h/2-60:
      alpha='if(lt(t,0.6),0,min((t-0.6)*3\,1))',
    drawtext=fontfile=${FONT}:text='peptide optimization':fontcolor=0x00E676:fontsize=48:
      x=(w-text_w)/2:y=h/2+10:
      alpha='if(lt(t,0.9),0,min((t-0.9)*3\,1))',
    drawtext=fontfile=${FONT_LIGHT}:text='is here.':fontcolor=white@0.8:fontsize=44:
      x=(w-text_w)/2:y=h/2+80:
      alpha='if(lt(t,1.2),0,min((t-1.2)*3\,1))',
    drawbox=x='w/2-160':y='h/2+180':w=320:h=70:color=0x00E676:t=fill,
    drawtext=fontfile=${FONT}:text='GET EARLY ACCESS':fontcolor=0x0A0A0A:fontsize=30:
      x=(w-text_w)/2:y=h/2+200:
      alpha='if(lt(t,1.8),0,min((t-1.8)*3\,1))',
    drawtext=fontfile=${FONT_LIGHT}:text='scan.peptide.ai':fontcolor=0x00E676@0.6:fontsize=28:
      x=(w-text_w)/2:y=h/2+290:
      alpha='if(lt(t,2.2),0,min((t-2.2)*2\,1))'
  " \
  -c:v libx264 -pix_fmt yuv420p "$OUT/scenes/scene5.mp4"

# ══════════════════════════════════════════════════════════════════════════════
# CONCATENATE ALL SCENES
# ══════════════════════════════════════════════════════════════════════════════
echo "Concatenating scenes..."
cat > "$OUT/scenes/concat.txt" << 'CONCAT'
file 'scene1.mp4'
file 'scene2.mp4'
file 'scene3.mp4'
file 'scene4.mp4'
file 'scene5.mp4'
CONCAT

ffmpeg -y -f concat -safe 0 -i "$OUT/scenes/concat.txt" \
  -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p \
  -movflags +faststart \
  "$OUT/scan-peptide-ai-reel.mp4"

echo ""
echo "========================================="
echo "Instagram Reel generated successfully!"
echo "Output: $OUT/scan-peptide-ai-reel.mp4"
echo "========================================="
ls -lh "$OUT/scan-peptide-ai-reel.mp4"
