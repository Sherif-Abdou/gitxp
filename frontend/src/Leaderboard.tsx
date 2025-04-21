import { useEffect, useState } from 'react';
import { getLeaderboard } from './api/api';

export function Leaderboard() {
  const [leaderboardData, setLeaderboardData] = useState<[string, number][]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchLeaderboard = async () => {
      try {
        setIsLoading(true);
        const data = await getLeaderboard();
        console.log(data);
        setLeaderboardData(data);
        setError(null);
      } catch (err) {
        setError('Failed to load leaderboard data. Please try again later.');
        console.error('Error fetching leaderboard:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchLeaderboard();
  }, []);

  return (
    <div className="leaderboard-container">
      <h2 className="leaderboard-title"> Rankings</h2>
      
      {isLoading && <div className="loading">Loading leaderboard data...</div>}
      
      {error && <div className="error-message">{error}</div>}
      
      {!isLoading && !error && (
        leaderboardData.length > 0 ? (
          <div className="leaderboard-table">
            <div className="leaderboard-header">
              <div className="rank-column">Rank</div>
              <div className="name-column">Name</div>
              <div className="score-column">XP</div>
            </div>
            
            {leaderboardData.map(([name, score], index) => (
              <div 
                key={name} 
                className={`leaderboard-row ${index % 2 === 0 ? 'even-row' : 'odd-row'}`}
              >
                <div className="rank-entry">{index + 1}</div>
                <div className="name-entry">{name}</div>
                <div className="score-entry">{score}</div>
              </div>
            ))}
          </div>
        ) : (
          <div className="no-data">No leaderboard data available</div>
        )
      )}
    </div>
  );
}
