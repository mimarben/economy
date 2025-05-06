import { Component, OnInit } from '@angular/core';
import { AccountBase as Account } from '../../../models/AccountBase';
import { GenericTableComponent, TableColumn } from '../../shared/generic-table/generic-table.component'; // Ajusta la ruta según tu estructura


@Component({
  selector: 'app-accounts',
  imports: [GenericTableComponent],
  templateUrl: './accounts.component.html',
  styleUrls: ['./accounts.component.css']
})
export class AccountsComponent implements OnInit {
  accounts: Account[] = [];
  isLoading = false;
  errorMessage = '';

  columns: TableColumn<Account>[] = [
    { key: 'id', label: 'ID', sortable: true },
    { key: 'name', label: 'Name', sortable: true },
    { key: 'description', label: 'Description', sortable: false },
    { key: 'iban', label: 'IBAN', sortable: true },
    { key: 'balance', label: 'Balance', sortable: true },
    { key: 'active', label: 'Active', sortable: true, formatter: (v) => v ? 'Yes' : 'No' },
    { key: 'bank_id', label: 'Bank ID', sortable: true },
    { key: 'user_id', label: 'User ID', sortable: true },
  ];

  constructor() {}

  ngOnInit() {
    this.loadAccounts();
  }

  loadAccounts() {
    this.isLoading = true;
    // Ejemplo de cómo cargar las cuentas desde un servicio:
    // this.accountService.getAccounts().subscribe({
    //   next: (data) => {
    //     this.accounts = data;
    //     this.isLoading = false;
    //   },
    //   error: (err) => {
    //     this.errorMessage = 'Error loading accounts';
    //     this.isLoading = false;
    //   }
    // });

    // Ejemplo con datos mock (elimina esto cuando uses el servicio)
    this.accounts = [
      { id: 1, name: 'Main Account', description: 'Primary account', iban: 'ES1234567890', balance: 1000, active: true, bank_id: 1, user_id: 1 },
      { id: 2, name: 'Savings', description: 'For savings', iban: 'ES0987654321', balance: 5000, active: true, bank_id: 1, user_id: 1 },
    ];
    this.isLoading = false;
  }

  editAccount(account: Account) {
    // Lógica para editar (abre un diálogo, por ejemplo)
    console.log('Edit account:', account);
    // const dialogRef = this.dialog.open(AccountFormDialogComponent, { data: account });
    // dialogRef.afterClosed().subscribe(result => { ... });
  }

  addAccount() {
    // Lógica para añadir una cuenta
    console.log('Add new account');
    // const dialogRef = this.dialog.open(AccountFormDialogComponent, { data: { id: null, name: '', ... } });
    // dialogRef.afterClosed().subscribe(result => { ... });
  }
}
