import { CategoryRule } from "@app/models/import/category-rule.model";

export const CATEGORY_RULES: CategoryRule[] = [

  {
    keywords: ["carrefour", "mercadona", "lidl", "dia"],
    categoryName: "Supermercado",
    type: "expense"
  },

  {
    keywords: ["amazon"],
    categoryName: "Compras",
    type: "expense"
  },

  {
    keywords: ["uber", "cabify"],
    categoryName: "Transporte",
    type: "expense"
  },

  {
    keywords: ["netflix", "spotify"],
    categoryName: "Suscripciones",
    type: "expense"
  }
  ,
  {
    keywords: ["o2", "fibra"],
    categoryName: "Internet",
    type: "expense"
  }
  ,
  {
    keywords: ["sheel", "repsol"],
    categoryName: "Gasolina",
    type: "expense"
  }
  ,
  {
    keywords: ["COLEGIO", "AGUSTINAS"],
    categoryName: "Colegio Agustinas",
    type: "expense"
  }
  ,
  {
    keywords: ["KIDS"],
    categoryName: "Kids&Us",
    type: "expense"
  }
  ,
  {
    keywords: ["nómina","pysco","avl"],
    categoryName: "Nómina",
    type: "income"
  },
  {
    keywords: ["CURENERG?A COMERCIALIZADOR ?LTIMO"],
    categoryName: "Gas",
    type: "income"    
  }

];