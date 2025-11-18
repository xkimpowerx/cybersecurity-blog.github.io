// NAVER is a popular South Korean search engine
const NAVER_SEARCH_URL = 'https://search.naver.com/search.naver';

export function initVideoSearch() {
    const searchInput = document.getElementById('search-input');
    const searchButton = document.getElementById('search-button');
    const resultsContainer = document.getElementById('results-container');

    searchButton.addEventListener('click', () => {
        const query = searchInput.value.trim();
        if (query) {
            searchVideos(query);
        }
    });

    async function searchVideos(query) {
        try {
            const response = await fetch(`${NAVER_SEARCH_URL}?where=video&query=${encodeURIComponent(query)}`);
            const html = await response.text();
            console.log('Fetched HTML:', html.substring(0, 500)); // Log first 500 characters of the response

            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            
            // Try a more general selector
            const videoItems = doc.querySelectorAll('.video_item');
            console.log('Found video items:', videoItems.length);

            if (videoItems.length === 0) {
                console.log('DOM structure:', doc.body.innerHTML.substring(0, 1000));
            }

            displayResults(Array.from(videoItems).slice(0, 10));
        } catch (error) {
            console.error('Error fetching videos:', error);
        }
    }

    function displayResults(videos) {
        resultsContainer.innerHTML = '';
        videos.forEach(video => {
            const title = video.querySelector('.title_link')?.textContent.trim() || 'No title';
            const thumbnailUrl = video.querySelector('.thumb_area img')?.src || '';
            const channelTitle = video.querySelector('.channel')?.textContent.trim() || 'Unknown channel';
            const videoUrl = video.querySelector('.title_link')?.href || '#';
            const duration = video.querySelector('.time')?.textContent.trim() || '';

            const videoItem = document.createElement('div');
            videoItem.classList.add('video-item');
            videoItem.innerHTML = `
                <img src="${thumbnailUrl}" alt="${title}">
                <h3>${title}</h3>
                <p>${channelTitle}</p>
                <p>Duration: ${duration}</p>
                <a href="${videoUrl}" target="_blank">Watch Video</a>
            `;
            resultsContainer.appendChild(videoItem);
        });
    }
}
