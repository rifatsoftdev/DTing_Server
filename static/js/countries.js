import { ApiClient } from "./ApiClient.js";

const BASE_URL = window.location.origin;
const api = new ApiClient(BASE_URL);


async function get_countries() {
    try {
        const response = await api.get("/country/counties");
        window.countries = response.data?.countries || [];
        return response.data?.countries || [];
    } catch (error) {
        console.error('Error loading countries from ISO3166 API:', error);
        return [];
    }
}

export async function loadCountries(selectElement) {
    try {
        const countries = await get_countries();
        
        if (selectElement) {
            selectElement.innerHTML = "";
            
            countries.forEach(country => {
                const option = document.createElement("option");
                option.value = country.country_code;
                option.textContent = `${country.flag_emoji || ''} ${country.country_name || ''} ${country.country_code}`;
                selectElement.appendChild(option);
            });
            
            if (countries.length > 0) {
                selectElement.selectedIndex = 0;
            }
        }
    } catch (error) {
        console.error('Error loading countries:', error);
        if (selectElement) {
            selectElement.innerHTML = '<option value="" disabled>Error loading countries</option>';
        }
    }
}


window.loadCountries = loadCountries;
window.get_countries = get_countries;