document.addEventListener("DOMContentLoaded", function() {
  const movieInput = document.getElementById("movie-input");
  const recommendBtn = document.getElementById("recommend-btn");
  const movieContainer = document.getElementById("movie-container");

  // Function to handle recommendation fetching
  recommendBtn.addEventListener("click", function() {
      const movieName = movieInput.value.trim();
      if (!movieName) {
          alert("Please enter a movie name!");
          return;
      }

      fetch(`http://3.224.55.96:5000/recommend?movie=${encodeURIComponent(movieName)}`)
          .then(response => response.json())
          .then(data => {
              if (data.error) {
                  movieContainer.innerHTML = `<p>${data.error}</p>`;
              } else {
                  const recommendations = data.recommended_movies;
                  movieContainer.innerHTML = ""; // Clear previous results

                  recommendations.forEach(movie => {
                      const movieElement = document.createElement("div");
                      movieElement.classList.add("movie-item");

                      const movieImage = document.createElement("img");
                      movieImage.src = movie.image_url;
                      movieImage.alt = movie.title;

                      const movieTitle = document.createElement("h3");
                      movieTitle.textContent = movie.title;

                      movieElement.appendChild(movieImage);
                      movieElement.appendChild(movieTitle);
                      movieContainer.appendChild(movieElement);
                  });
              }
          })
          .catch(error => {
              movieContainer.innerHTML = `<p>Error fetching recommendations: ${error.message}</p>`;
          });
  });
});
