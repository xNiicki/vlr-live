"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

interface Map {
    name: string;
    pick: string;
    team1_score: string;
    team2_score: string;
    time: string;
}

interface Stream {
    link: string;
    name: string;
}

interface Match {
    event: string;
    maps: Map[];
    stage: string;
    status: string;
    streams: Stream[];
    team1: string;
    team1_logo: string;
    team1_score: string;
    team2: string;
    team2_logo: string;
    team2_score: string;
}

export default function MatchDetails() {
    const { id } = useParams();
    const [match, setMatch] = useState<Match | null>(null);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (id) {
            const fetchMatchDetails = async () => {
                try {
                    const response = await fetch(`http://localhost:9091/match/${id}`);
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    const result = await response.json();
                    setMatch(result);
                } catch (error) {
                    console.error("Error fetching match details:", error);
                    setError("Load Failed");
                }
            };

            fetchMatchDetails();
            const intervalId = setInterval(fetchMatchDetails, 3000);

            return () => clearInterval(intervalId);
        }
    }, [id]);

    if (error) {
        return <div>Error: {error}</div>;
    }

    if (!match) {
        return (
            <div className="flex justify-center items-center min-h-screen">
                <div className="spinner"></div>
            </div>
        );
    }

    return (
        <div className="flex flex-col items-center min-h-screen p-8 pb-20 gap-4 sm:p-20 font-[family-name:var(--font-geist-sans)] bg-background">
            <div className="match p-4 border rounded shadow-md w-full max-w-4xl bg-background text-gray-200">
                <div className="flex justify-between items-center mb-4">
                    <div className="flex items-center space-x-2">
                        <img src={match.team1_logo} alt={`${match.team1} logo`} className="w-12 h-12" />
                        <span className="text-xl font-bold">{match.team1}</span>
                    </div>
                    <span className="text-xl font-bold">{match.team1_score}</span>
                </div>
                <div className="flex justify-between items-center mb-4">
                    <div className="flex items-center space-x-2">
                        <img src={match.team2_logo} alt={`${match.team2} logo`} className="w-12 h-12" />
                        <span className="text-xl font-bold">{match.team2}</span>
                    </div>
                    <span className="text-xl font-bold">{match.team2_score}</span>
                </div>
                <p className={`eta ${match.status === 'live' ? 'live' : ''} text-lg`}><strong>Status:</strong> {match.status}</p>
                <p className="text-lg"><strong>Event:</strong> {match.event}</p>
                <p className="text-lg"><strong>Stage:</strong> {match.stage}</p>
                <div className="mt-4">
                    <h3 className="text-2xl font-bold mb-2">Maps:</h3>
                    {match.maps.map((map, index) => (
                        <div key={index} className="map mb-4 p-4 border rounded bg-neutral-900 text-gray-200">
                            <p className="text-lg"><strong>Map:</strong> {map.name}</p>
                            <p className="text-lg"><strong>Pick:</strong> {map.pick}</p>
                            <p className="text-lg"><strong>Score:</strong> {map.team1_score} - {map.team2_score}</p>
                            <p className="text-lg"><strong>Time:</strong> {map.time}</p>
                        </div>
                    ))}
                </div>
                <div className="mt-4">
                    <h3 className="text-2xl font-bold mb-2">Streams:</h3>
                    {match.streams.map((stream, index) => (
                        <div key={index} className="stream mb-2">
                            <a href={stream.link} target="_blank" rel="noopener noreferrer" className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 transition duration-300 ease-in-out">{stream.name}</a>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}