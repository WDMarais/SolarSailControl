import os
import bpy

homeDir = "/home/wdmarais/Desktop/blenderSpaceSim/KeplerElements/"
renderDir = homeDir + "renders/"
outputDir = homeDir + "movies/"
files = os.listdir(renderDir)
files.sort()

scene = bpy.context.scene

scene.sequence_editor_create()

seq = scene.sequence_editor.sequences.new_image(
        name="MyStrip",
        filepath=os.path.join(renderDir, files[0]),
        channel=1, frame_start=1)

# add the rest of the images.
i = 1
for f in files[1:]:
    i += 1
    seq.elements.append(f)

scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 50
scene.render.image_settings.file_format = 'H264'
scene.render.ffmpeg.format = 'MPEG4'
scene.render.fps = 60
scene.frame_start = 1
scene.frame_end = i
scene.render.filepath = outputDir + "movie.mp4"
scene.render.use_sequencer = True
print(seq.elements)
bpy.ops.render.render(use_viewport = False, animation=True)