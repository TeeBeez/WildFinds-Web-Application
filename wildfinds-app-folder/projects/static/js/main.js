// Add an event listener to handle delete actions
document.addEventListener('click', function (e) {
    if (e.target.classList.contains('delete-post')) {
        const postId = e.target.dataset.postId;

        if (confirm('Are you sure you want to delete this post?')) {
            // Send a DELETE request to the server
            fetch(`/delete_post/${postId}`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').getAttribute('content'),
                }
            })
                .then(response => {
                    if (response.ok) {
                        // Remove the post from the page
                        document.querySelector(`#post-${postId}`).remove();
                        alert('Post deleted successfully.');
                    } else {
                        alert('Failed to delete post.');
                    }
                })
                .catch(error => console.error('Error:', error));
        }
    }
});

// Add an event listener to handle edit actions
document.addEventListener('click', function (e) {
    if (e.target.classList.contains('edit-post')) {
        const postId = e.target.dataset.postId;
        const caption = prompt('Enter a new caption:');

        if (caption) {
            // Send an UPDATE request to the server
            fetch(`/edit_post/${postId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').getAttribute('content'),
                },
                body: JSON.stringify({ caption: caption })
            })
                .then(response => {
                    if (response.ok) {
                        // Update the caption on the page
                        document.querySelector(`#post-${postId} .post-caption h4`).textContent = caption;
                        alert('Caption updated successfully.');
                    } else {
                        alert('Failed to update caption.');
                    }
                })
                .catch(error => console.error('Error:', error));
        }
    }
});


let autocomplete = new google.maps.places.Autocomplete(document.getElementById('city'), {
    types: ['(cities)'],
    componentRestrictions: { country: 'us' },  // You can restrict to a specific country
});

autocomplete.addListener('place_changed', function() {
    var place = autocomplete.getPlace();

    if (!place.geometry) {
        console.log("Place details are not available.");
        return;
    }

    // Get the city name
    var city = place.name;

    // Get latitude and longitude
    var lat = place.geometry.location.lat();
    var lng = place.geometry.location.lng();

    // Set the city, lat, and lng in hidden fields for submission
    document.getElementById('city_input').value = city;
    document.getElementById('latitude_input').value = lat;
    document.getElementById('longitude_input').value = lng;
});

let page = 1;
const postContainer = document.getElementById('post-container');
const loadingIndicator = document.getElementById('loading');

const loadPosts = async () => {
    loadingIndicator.style.display = 'block';

    try {
        const response = await fetch(`/explore_posts?page=${page}`);
        const posts = await response.json();

        posts.forEach(post => {
            const postElement = document.createElement('div');
            postElement.classList.add('post');
            postElement.innerHTML = `
                <img src="${post.photo}" alt="Post Image" class="post-image">
                <div class="post-details">
                <p>${post.caption}</p>
                <p>@${post.username}</p>
                <p>${post.city} - ${post.date_posted}</p>
            </div>
            `;
            postContainer.appendChild(postElement);
        });

        if (posts.length === 0) {
            // No more posts to load
            window.removeEventListener('scroll', handleScroll);
        }

        page++;
    } catch (error) {
        console.error('Error loading posts:', error);
    } finally {
        loadingIndicator.style.display = 'none';
    }
};

const handleScroll = () => {
    if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 100) {
        loadPosts();
    }
};



window.addEventListener('scroll', handleScroll);
loadPosts(); // Initial load



