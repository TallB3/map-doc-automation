looking at the transcript.txt file, i can see that the 15-second markers are implemented wrong.
Let me explain why i got them in the first place:

Before having them, i was only able to understand at what time of the video something was said when the speakers switched. cuz the structure looks something like this:

[00:00:00] speaker_0:
Hi, how are you?

[00:00:05] speaker_1:
Good, good, how are you mate?

but what happens if a certain speaker talks for a long period of time? their line is going to go on and on, and we are going to lose the ability to know when something was said. The only time we are going to get a timestamp is when a speaker switches. 

this is why i wanted to have the 15-sec markers. the purpose was to let us keep track of time when the same speaker talks for a long period of time. 

but looking how it's implemented now, it seems like there is a 15-sec marker EVERY 15 seconds, regardless on the speakers speech duration. 

I dont want it to be like that. i want the 15-sec markers to appear only when a speaker talks for more than 15 seconds straight!
