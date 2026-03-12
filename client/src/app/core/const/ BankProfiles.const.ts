import { BankProfile } from "@app/models/import/BankProfile";

export const BANK_PROFILES: BankProfile[] = [

  {
    id: "ing",
    name: "ING",
    headerKeywords: ["fecha", "concepto", "importe"],
    headerRowGuess: 4
  },

  {
    id: "bbva",
    name: "BBVA",
    headerKeywords: ["fecha", "descripcion", "importe"]
  },

  {
    id: "santander",
    name: "Santander",
    headerKeywords: ["fecha operacion", "concepto", "importe"]
  }

];