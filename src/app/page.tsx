"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

interface Match {
    eta: string;
    event: string;
    match_id: string;
    stage: string;
    team1: string;
    team1_flag: string;
    team1_score: string;
    team2: string;
    team2_flag: string;
    team2_score: string;
    time: string;
}

export default function Home() {
    const [data, setData] = useState<Match[] | null>(null);
    const router = useRouter();

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await fetch("http://localhost:9091/matches");
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const result = await response.json();
                setData(result);
            } catch (error) {
                console.error("Error fetching data:", error);
            }
        };

        fetchData(); // Initial fetch
        const interval = setInterval(fetchData, 3000); // Fetch every 3 seconds

        return () => clearInterval(interval); // Cleanup on unmount
    }, []);

    const handleMatchClick = (matchId: string) => {
        router.push(`/matches/${matchId}`);
    };

    return (
        <div className="flex flex-col items-center min-h-screen p-8 pb-20 gap-4 sm:p-20 font-[family-name:var(--font-geist-sans)]">
            {data ? (
                data.map((match, index) => (
                    <div
                        key={index}
                        className="match p-4 border rounded shadow-md w-full max-w-md cursor-pointer"
                        onClick={() => handleMatchClick(match.match_id)}
                    >
                        <div className="flex flex-col mb-2">
                            <div className="flex justify-between items-center">
                                <span className="flex items-center space-x-2">
                                    <img src={`https://flagcdn.com/16x12/${match.team1_flag.replace('mod-', '')}.png`} alt={`${match.team1} flag`} />
                                    {match.team1}
                                </span>
                                <span>{match.team1_score}</span>
                            </div>
                            <div className="flex justify-between items-center">
                                <span className="flex items-center space-x-2">
                                    <img src={`https://flagcdn.com/16x12/${match.team2_flag.replace('mod-', '')}.png`} alt={`${match.team2} flag`} />
                                    {match.team2}
                                </span>
                                <span>{match.team2_score}</span>
                            </div>
                        </div>
                        <p className={`eta ${match.eta === 'LIVE' ? 'live' : ''}`}><strong>ETA:</strong> {match.eta}</p>
                        <p><strong>Event:</strong> {match.event}</p>
                        <p><strong>Stage:</strong> {match.stage}</p>
                        <p><strong>Time:</strong> {match.time}</p>
                    </div>
                ))
            ) : (
                <div>Loading...</div>
            )}
        </div>
    );
}