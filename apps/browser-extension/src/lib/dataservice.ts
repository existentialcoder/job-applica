

class JALocalStorage {
    static getItem(key: string): string | null {
        return localStorage.getItem(key);
    }
    static setItem(key: string, value: string): void {
        localStorage.setItem(key, value);
    }
    static removeItem(key: string): void {
        localStorage.removeItem(key);
    }
};

export default {
    getUserName(): string {
        const userName = JALocalStorage.getItem('userName') || 'Guest';

        return userName;
    },
    getAppSettings(): object {
        const appSettings = JALocalStorage.getItem('appSettings');
        return appSettings ? JSON.parse(appSettings) : {};
    },
}
