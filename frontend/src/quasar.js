// src/quasar.js
import { Quasar, Notify, Dialog } from 'quasar'

export default {
  install(app) {
    app.use(Quasar, {
      plugins: {
        Notify, // Enable Notify Plugin
        Dialog, // Enable Dialog Plugin
      },
      config: {
        notify: { /* default settings */ },
      },
    })
  }
}
