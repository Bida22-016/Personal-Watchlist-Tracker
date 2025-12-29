// Box Office Data Fetcher for Static Sites (GitHub Pages)
// Works directly in the browser - no backend needed!

class BoxOfficeFetcher {
  constructor(omdbKey = null, tmdbKey = null) {
    this.omdbKey = omdbKey;
    this.tmdbKey = tmdbKey;
    this.omdbBase = 'https://www.omdbapi.com/';
    this.tmdbBase = 'https://api.themoviedb.org/3';
  }

  async fetchOMDB(title = null, imdbId = null) {
    if (!this.omdbKey) {
      return { error: 'OMDB API key required' };
    }

    const params = new URLSearchParams({
      apikey: this.omdbKey
    });

    if (imdbId) {
      params.append('i', imdbId);
    } else if (title) {
      params.append('t', title);
    } else {
      return { error: 'Provide either title or imdbId' };
    }

    try {
      const response = await fetch(`${this.omdbBase}?${params}`);
      const data = await response.json();

      if (data.Response === 'True') {
        return {
          title: data.Title,
          year: data.Year,
          boxOffice: data.BoxOffice || 'N/A',
          imdbRating: data.imdbRating,
          imdbId: data.imdbID,
          plot: data.Plot,
          poster: data.Poster
        };
      } else {
        return { error: data.Error };
      }
    } catch (error) {
      return { error: `Request failed: ${error.message}` };
    }
  }

  async fetchTMDB(movieId = null, title = null) {
    if (!this.tmdbKey) {
      return { error: 'TMDB API key required' };
    }

    // Search for movie if title provided
    if (title && !movieId) {
      try {
        const searchParams = new URLSearchParams({
          api_key: this.tmdbKey,
          query: title
        });
        
        const searchResponse = await fetch(`${this.tmdbBase}/search/movie?${searchParams}`);
        const searchData = await searchResponse.json();

        if (!searchData.results || searchData.results.length === 0) {
          return { error: 'Movie not found' };
        }

        movieId = searchData.results[0].id;
      } catch (error) {
        return { error: `Search failed: ${error.message}` };
      }
    }

    if (!movieId) {
      return { error: 'Provide either movieId or title' };
    }

    // Get movie details
    try {
      const params = new URLSearchParams({ api_key: this.tmdbKey });
      const response = await fetch(`${this.tmdbBase}/movie/${movieId}?${params}`);
      const data = await response.json();

      return {
        title: data.title,
        year: data.release_date?.substring(0, 4),
        revenue: `$${data.revenue?.toLocaleString() || 0}`,
        budget: `$${data.budget?.toLocaleString() || 0}`,
        tmdbRating: data.vote_average,
        tmdbId: data.id,
        overview: data.overview,
        posterPath: data.poster_path ? `https://image.tmdb.org/t/p/w500${data.poster_path}` : null
      };
    } catch (error) {
      return { error: `Request failed: ${error.message}` };
    }
  }

  async fetchMultiple(titles) {
    const results = [];
    for (const title of titles) {
      let result;
      if (this.omdbKey) {
        result = await this.fetchOMDB(title);
      } else if (this.tmdbKey) {
        result = await this.fetchTMDB(null, title);
      } else {
        result = { error: 'No API key provided' };
      }
      results.push({ [title]: result });
    }
    return results;
  }
}

// Example usage in HTML
/*
<!DOCTYPE html>
<html>
<head>
  <title>Movie Box Office</title>
</head>
<body>
  <h1>Movie Box Office Search</h1>
  
  <input type="text" id="movieTitle" placeholder="Enter movie title">
  <button onclick="searchMovie()">Search</button>
  
  <div id="results"></div>

  <script src="boxoffice.js"></script>
  <script>
    // Initialize with your API keys
    const fetcher = new BoxOfficeFetcher(
      'YOUR_OMDB_KEY',  // Get from http://www.omdbapi.com/apikey.aspx
      'YOUR_TMDB_KEY'   // Get from https://www.themoviedb.org/settings/api
    );

    async function searchMovie() {
      const title = document.getElementById('movieTitle').value;
      const resultsDiv = document.getElementById('results');
      
      resultsDiv.innerHTML = '<p>Loading...</p>';
      
      // Fetch from OMDB
      const result = await fetcher.fetchOMDB(title);
      
      if (result.error) {
        resultsDiv.innerHTML = `<p>Error: ${result.error}</p>`;
      } else {
        resultsDiv.innerHTML = `
          <h2>${result.title} (${result.year})</h2>
          <p><strong>Box Office:</strong> ${result.boxOffice}</p>
          <p><strong>IMDB Rating:</strong> ${result.imdbRating}</p>
          <p><strong>Plot:</strong> ${result.plot}</p>
          ${result.poster !== 'N/A' ? `<img src="${result.poster}" alt="${result.title}">` : ''}
        `;
      }
    }

    // Or fetch multiple movies on page load
    async function loadPopularMovies() {
      const movies = ['Inception', 'The Dark Knight', 'Interstellar'];
      const results = await fetcher.fetchMultiple(movies);
      console.log(results);
    }
  </script>
</body>
</html>
*/

// For Node.js/ES6 modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = BoxOfficeFetcher;
}