# How does our current workflow regarding post-production looks like:

1. Our studio technicions upload the mp4/mp3/wav to a google drive (from now on - gdrive)
2. We send the dgrive url link of the media source to create an elevenlabs transcript. we do it using a hugging face space called the valuebell transcriber. i urge you to visit ~/dev/valuebell-transcriber to see the code and understand how it all works
3. the valuebell transcriber is basically a wrapper around the elevenlabs api, which generates a transcript in a json file, but also code creates a more human readable transcript. you can find it in the code inside the directory i mentioned earlier.
4. then we download the human-readable transcript and upload it to gemini for creating the mapping doc. we do it using custom gems - which are similar to claude/chatgpt "projects" - where you basically add instructions and files to a gem/project and then when you conversate with it, it has all the provided info as context. so in our case, the instrutions are what we expect to have in the mapping doc - the exact instructions. we also add a bunch of files - past map-docs that we liked. when we open a conversation - we just feed it the transcript, and maybe tell it something like who was the guest in this epsidode, what show it belonged to, etc.
5. we save the generated map doc in the gdrive
6. our editors go in the file, the download the mp4 and they look at the map-doc. it gives them a brief about the episode, and tells them where they need to look for potential good reels. 
7. our editors edit using the suggestions - and upload their outputs to the gdrive.
8. we manually uplaod all of the materials in the google drive to youtube and spotify for creators (spotify's hosting platform - formally anchor.) we select titles, banners, episodes description etc based on the map-doc suggestions.

# How do i want it to eventually look - my end goal

1. Our studio technicions upload the mp4/mp3/wav to a google drive (from now on - gdrive)
2. code creates transcription  automatically
3. transcript sent to Gemini Pro 2.5 using google gemini api to create the map-doc
4. also, needs to create a json file that includes the reels suggestions, with the timestamps and suggested titles for the reels/shorts
5. code using the json and ffmpeg to cut clips to make human editors work faster by already giving them roughly the cuts they need, so they might not need to download the full episode.
6. upload all of the products to the gdrive, in nice folders
7. upload mp4 to youtube as a draft using youtube api, with episode title and descriptions as the map-doc suggests
8. open task in notion telling me to add a thumbnail
9. open task in notion telling me to upload the epiosde to spotify and give me all the info i need inside the task. this is because spotify doesnt have an api for uploads and such

# What i need from you in the short term

1. visit ~/dev/valuebell-transcriber like i suggested
2. Create a claude.md file with all of the relevant info i just mentioned and you gathered
3. set up git locally, create a porject in github called map-doc-automation and connect us to it
4. start working on a short term plan. we are not thinking about youtube/notion integration yet, but we definitely need to start cracking the gdrive integration and working with gemini api we also have to make the clip editing with ffmpeg work. i need you to present a plan of these initial stages. you will instruct me what i need to do to help you set up the integration, you would lay out the implementation plan, you would suggest how would the env that we build in would look like, and you would not write any code before we agree on the plan! 
