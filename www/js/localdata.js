class LocalData {
  constructor() {
  }

  get(key) {
    return localStorage.getItem(key);
  }

  set(key, val) {
    return localStorage.setItem(key, val);
  }

  remove(key) {
    localStorage.removeItem(key);
  }

  clear() {
    localStorage.clear();
  }
}
var LOCAL = new LocalData()


function set_auto_login(api) {
    LOCAL.set("autologin", api)
}


function get_auto_login() {
    return LOCAL.get("autologin")
}

function unset_auto_login() {
    LOCAL.remove("autologin")
}
