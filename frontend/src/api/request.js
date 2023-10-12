import axios from "axios"

const client = (() => {
    return axios.create({
        baseURL: "http://localhost:8000"
    });
})();

const request = async function (options, store) {
    const onSuccess = function (response) {
        return response.data;
    };

    const onError = function (error) {
        return Promise.reject(error.response);
    };

    return client(options).then(onSuccess).catch(onError);
};

export default request;