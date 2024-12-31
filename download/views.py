from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from .forms import ResponseForm
import logging
from youtube.utils.download import VideoDownloader


logger = logging.getLogger(__name__)

def submit_form(request):
    if request.method == 'POST':
        form = ResponseForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']
            try:
                # Initialize the downloader
                downloader = VideoDownloader()
                logger.info(f"Starting download for URL: {url}")
                
                # Attempt to download
                result = downloader.download_video(url)
                logger.info(f"Download result: {result}")
                
                if result['success']:
                    # Log success and redirect
                    logger.info(f"Successfully downloaded video: {result['filename']}")
                    return redirect('video_page', video_path=result['filename'])
                else:
                    # Log error and show message
                    logger.error(f"Download failed: {result['error']}")
                    messages.error(request, f"Download failed: {result['error']}")
            except Exception as e:
                logger.exception("Unexpected error during download")
                messages.error(request, f"An unexpected error occurred: {str(e)}")
    else:
        form = ResponseForm()
    
    return render(request, 'formsubmit/submit_form.html', {'form': form})

def video_page(request, video_path):
    logger.info(f"Accessing video page for: {video_path}")
    return render(request, 'formsubmit/video_page.html', {
        'video_name': video_path,
        'video_path': f"/media/videos/{video_path}",
    })