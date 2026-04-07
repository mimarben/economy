import { Component, OnInit, OnDestroy, ChangeDetectorRef } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { FormFieldConfig } from '@shared/generic-form/form-config';
import { GenericDialogComponent } from '@shared/generic-dialog/generic-dialog.component';
import { CardBase as Card } from '@cards_models/CardBase';
import { CardService } from '@app/services/cards/cards.service';
import { AccountBase as Account } from '@finance_models/AccountBase';
import { ToastService } from '@app/services/core/toast.service';
import { AccountService } from '@finance_services/account.service';
import { FormFactoryService } from '@app/core/factories/form-factory.service';
import {
  GenericTableComponent,
  TableColumn,
} from '@app/shared/components/generic-table/generic-table.component';
import { ApiResponse } from '@app/models/core/APIResponse';
import { environment } from '@env/environment';
import { MetaService } from '@core_services/meta.service';
import { forkJoin } from 'rxjs';
import { ImportOriginBase as ImportOrigin } from '@import_models/import-originBase';
import { ImportProfileBase as ImportProfile } from '@import_models/import-profileBase';
import { ImportOriginsService, ImportProfilesService } from '@import_services/import-profiles.service';

@Component({
  standalone: true,
  selector: 'app-cards',
  imports: [GenericTableComponent],
  templateUrl: './cards.component.html',
  styleUrl: './cards.component.scss',
})
export class CardsComponent {
  cards: Card[] = [];
  accounts: Account[] = [];
  origins: ImportOrigin[] = [];
  profiles: ImportProfile[] = [];
  filterValue = '';
  isLoading = false;
  errorMessage = '';
  formFields: FormFieldConfig[] = [];
  isFormValid = false;
  columns: TableColumn<Card>[] = [];
  accountMap: Record<number, string> = {};
  constructor(
    private cardService: CardService,
    private cdr: ChangeDetectorRef,
    private dialog: MatDialog,
    private toastService: ToastService,
    private formFactory: FormFactoryService,
    private accountService: AccountService,
    private metaService: MetaService,
    private importOriginsService: ImportOriginsService,
    private importProfilesService: ImportProfilesService,
  ) {}

  ngOnInit(): void {
    this.loadInitialData();
  }

  loadInitialData() {
    this.isLoading = true;
    forkJoin({
      cards: this.cardService.getAll(),
      accounts: this.accountService.getAll(),
      origins: this.importOriginsService.getOrigins(),
      profiles: this.importProfilesService.getProfiles(),
      meta: this.metaService.getMeta('card'),
    }).subscribe({
      next: ({ cards, accounts, origins, profiles, meta }) => {
        this.cards = cards.response;
        this.accounts = accounts.response;
        this.origins = origins.response;
        this.profiles = profiles.response;
        this.formFields = this.formFactory.enrichMetadataFields(meta.fields, {
          account: this.accounts.map((a) => ({
            value: a.id!,
            label: a.name,
          })),
          account_id: this.accounts.map((a) => ({
            value: a.id!,
            label: a.name,
          })),
          'import-origin': this.origins.map((origin) => ({
            value: origin.id,
            label: origin.name,
          })),
          import_origin_id: this.origins.map((origin) => ({
            value: origin.id,
            label: origin.name,
          })),
          'import-profile': this.profiles.map((profile) => ({
            value: profile.id,
            label: profile.name,
          })),
          import_profile_id: this.profiles.map((profile) => ({
            value: profile.id,
            label: profile.name,
          })),
        });
        console.log('META FIELDS', this.formFields);
        this.accountMap = this.accounts.reduce(
          (acc, account) => {
            acc[account.id!] = account.name;
            return acc;
          },
          {} as Record<number, string>,
        );

        this.columns = this.formFactory.getTableColumnsFromMetadata<Card>(
          this.formFields,
        );

        this.enrichColumns(); // 👈 se queda por ahora

        this.isLoading = false;
      },
      error: () => {
        this.errorMessage = 'Error loading data';
        this.isLoading = false;
      },
    });
  }
  private enrichColumns() {
    if (!this.columns || this.columns.length === 0) return;
    this.columns = this.columns.map((col) => {
      if (col.key === 'account_id') {
        return {
          ...col,
          formatter: (value: number) => {
            return this.accountMap[value] || '—';
          },
        };
      }
      return col;
    });
  }

  editCard(card: Card): void {
    this.openDialog(card);
  }

  addCard(): void {
    this.openDialog();
  }

  openDialog(data?: Card): void {
    const dialogRef = this.dialog.open(GenericDialogComponent, {
      data: {
        title: data ? 'Edit Card' : 'New Card',
        fields: this.formFields,
        initialData: data || {},
      },
    });

    dialogRef.afterClosed().subscribe((result) => {
      if (data) {
        this.updateCard({ ...data, ...result });
      } else {
        this.createCard(result);
      }
    });
  }

  updateCard(card: Card): void {
    this.cardService.updateCard(card.id!, card).subscribe({
      next: (response: ApiResponse<Card>) => {
        this.isLoading = false;
        this.toastService.showToast(
          response,
          environment.toastType.Success,
          {},
        );
        const updatedCard = response.response;
        const index = this.cards.findIndex((acc) => acc.id === updatedCard.id);
        if (index !== -1) {
          this.cards[index] = updatedCard;
          this.cards = [...this.cards];
        }
        this.cdr.detectChanges();
      },
      error: (error: any) => {
        console.error('Error updating account:', error.error);
        this.isLoading = false;
        this.toastService.showToast(
          error.error as ApiResponse<string>,
          environment.toastType.Error,
          {},
        );
      },
    });
  }

  createCard(card: Card): void {
    this.cardService.createCard(card).subscribe({
      next: (response: ApiResponse<Card>) => {
        this.isLoading = false;
        this.toastService.showToast(
          response,
          environment.toastType.Success,
          {},
        );
        const newCard = response.response;
        this.cards.push(newCard); // Add the new card to the array
        this.cards = [...this.cards]; // Reassign to trigger change detection
        this.cdr.detectChanges();
      },
      error: (error: any) => {
        console.error('Error creating card:', error.error);
        this.isLoading = false;
        this.errorMessage = 'Failed to create card.';
        this.toastService.showToast(
          error.error as ApiResponse<string>,
          environment.toastType.Error,
          {},
        );
      },
    });
  }

  applyFilter(event: Event) {
    this.filterValue = (event.target as HTMLInputElement).value
      .trim()
      .toLowerCase();
  }
}
