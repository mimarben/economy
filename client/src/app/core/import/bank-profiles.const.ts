import { BankProfile } from "@import_models/BankProfile";

export const BANK_PROFILES: BankProfile[] = [

  {
    id: "ING",
    name: "ING Direct",
    headerRowGuess: 4,
    columns: {
      date: ["valor", "fecha"],
      description: ["descripcion", "descripción"],
      balance: ["saldo"],
      amount: ["importe"]
    }
  },

  {
    id: "Carrefour",
    name: "Carrefour Bank",
    headerRowGuess: 21,
    columns: {
      date: ["fecha"],
      description: ["concepto"],
      balance: ["saldo"],
      amount: ["cargo"],
    }
  },

  {
    id: "MyInvestor",
    name: "MyInvestor",
    headerRowGuess: 21,
    columns: {
      date: ["fecha"],
      description: ["concepto"],
       balance: ["saldo"],
      amount: ["cargo"]
    }
  },

  {
    id: "TradeRepublic",
    name: "TradeRepublic",
    headerRowGuess: 21,
    columns: {
      date: ["fecha"],
      description: ["concepto"],
       balance: ["saldo"],
      amount: ["cargo"]
    }
  },

  {
    id: "Criptan",
    name: "Criptan Trade",
    headerRowGuess: 21,
    columns: {
      date: ["fecha"],
      description: ["concepto"],
       balance: ["saldo"],
      amount: ["cargo"]
    }
  }


];