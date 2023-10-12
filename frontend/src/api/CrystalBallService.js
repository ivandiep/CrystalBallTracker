import request from "./request"

export default class CrystalBallService {
    static getMostPicked() {
        return request({
            url: "/champions/most-picked",
            method: "GET"
        });
    }
}