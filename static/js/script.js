document.addEventListener('DOMContentLoaded', function() {
    // Update the rating slider value display
    const ratingSlider = document.getElementById('min-rating');
    const ratingValue = document.getElementById('rating-value');
    
    ratingSlider.addEventListener('input', function() {
        ratingValue.textContent = this.value;
    });
    
    // Handle form submission
    const recommendationForm = document.getElementById('recommendation-form');
    const recommendationsContainer = document.getElementById('recommendations-container');
    const recommendationsList = document.getElementById('recommendations-list');
    const loadingIndicator = document.getElementById('loading');
    
    recommendationForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Show loading indicator
        loadingIndicator.style.display = 'block';
        recommendationsList.innerHTML = '';
        recommendationsContainer.style.display = 'block';
        
        // Get form values
        const genre = document.getElementById('genre').value;
        const runtime = document.getElementById('runtime').value;
        const age = document.getElementById('age').value;
        const minRating = document.getElementById('min-rating').value;
        const topN = document.getElementById('top-n').value;
        
        // Create request payload
        const payload = {
            genre: genre,
            runtime: runtime,
            age: parseInt(age),
            min_rating: parseFloat(minRating),
            top_n: parseInt(topN)
        };
        
        // Send request to backend
        fetch('/recommend', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        })
        .then(response => response.json())
        .then(data => {
            // Hide loading indicator
            loadingIndicator.style.display = 'none';
            
            if (data.success) {
                displayRecommendations(data.recommendations);
            } else {
                displayError(data.error);
            }
        })
        .catch(error => {
            loadingIndicator.style.display = 'none';
            displayError('An error occurred while fetching recommendations. Please try again.');
            console.error('Error:', error);
        });
    });
    
    function displayRecommendations(recommendations) {
        if (recommendations.length === 0) {
            recommendationsList.innerHTML = `
                <div class="col-12 text-center">
                    <p class="lead">No movies found matching your criteria. Try adjusting your preferences.</p>
                </div>
            `;
            return;
        }
        
        let html = '';
        
        recommendations.forEach(movie => {
            // Get runtime badge class based on category
            let runtimeBadgeClass = 'bg-primary';
            if (movie.runtime_category === 'short') {
                runtimeBadgeClass = 'bg-success';
            } else if (movie.runtime_category === 'long') {
                runtimeBadgeClass = 'bg-danger';
            }
            
            html += `
                <div class="col-md-6 col-lg-4 mb-4">
                    <div class="card movie-card">
                        <div class="card-body">
                            <h5 class="card-title">${movie.name} <span class="movie-year">(${movie.year})</span></h5>
                            <p class="movie-genre">${movie.genre}</p>
                            <div class="d-flex justify-content-between align-items-center mb-3">
                                <span class="movie-rating">★ ${movie.rating.toFixed(1)}</span>
                                <span class="badge ${runtimeBadgeClass}">${capitalizeFirstLetter(movie.runtime_category)}</span>
                            </div>
                            <p class="movie-tagline">${movie.tagline || 'No tagline available'}</p>
                        </div>
                    </div>
                </div>
            `;
        });
        
        recommendationsList.innerHTML = html;
        
        // Scroll to recommendations
        recommendationsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    
    function displayError(errorMessage) {
        recommendationsList.innerHTML = `
            <div class="col-12">
                <div class="alert alert-danger" role="alert">
                    ${errorMessage}
                </div>
            </div>
        `;
    }
    
    function capitalizeFirstLetter(string) {
        return string.charAt(0).toUpperCase() + string.slice(1);
    }
});