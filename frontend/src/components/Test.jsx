import { useQuery } from "react-query";
import CrystalBallService from "../api/CrystalBallService";

export default function Test() {
  const { data: mostPicked, isLoading: isLoadingPicks } = useQuery(["most-picked"], () => CrystalBallService.getMostPicked());

  const champs = isLoadingPicks ? [] : Object.entries(mostPicked);
  console.log(champs);
  return (
  <div>
    {champs.map(([key, val]) => 
        <h2 key={key}>{key}: {val}</h2>
      )}
  </div>
  )
}