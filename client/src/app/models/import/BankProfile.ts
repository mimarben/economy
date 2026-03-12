export interface BankProfile {

  id: string;

  name: string;

  headerRowGuess?: number;
  
  columns: {
    date: string[];
    description: string[];
    amount: string[];
    balance:string[];
  };

}