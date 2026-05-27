import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { forkJoin } from 'rxjs';
import { GenericDialogComponent } from '@shared/generic-dialog/generic-dialog.component';
import { HouseholdMemberBase as HouseHoldMember } from '@households_models/HouseholdMemberBase';
import { UserBase as User } from '@users_models/UserBase';
import { HouseholdBase as Household } from '@households_models/HouseholdBase';
import { GenericTableComponent, TableColumn } from '@shared/generic-table/generic-table.component';
import { ApiResponse } from '@app/models/core/APIResponse';
import { FormFactoryService } from '@app/core/factories/form-factory.service';
import { FormFieldConfig } from '@shared/generic-form/form-config';
import { ToastService } from '@core_services/toast.service';
import { environment } from '@env/environment';
import { HouseholdMemberService } from '@households_services/household-member.service';
import { UserService } from '@users_services/user.service';
import { HouseholdService } from '@households_services/household.service';
import { MetaService } from '@core_services/meta.service';

@Component({
  selector: 'app-householdmembers',
  imports: [GenericTableComponent],
  templateUrl: './household-members.component.html',
  styleUrl: './household-members.component.css',
})
export class HouseholdmembersComponent implements OnInit {
  houseHoldsMembers: HouseHoldMember[] = [];
  filterValue = '';
  isLoading = false;
  errorMessage = '';
  formFields: FormFieldConfig[] = [];
  isFormValid = false;
  columns: TableColumn<HouseHoldMember>[] = [];
  householdsMap: Record<number, string> = {};
  usersMap: Record<number, string> = {};

  constructor(
    private householdmemberService: HouseholdMemberService,
    private cdr: ChangeDetectorRef,
    private dialog: MatDialog,
    private toastService: ToastService,
    private formFactory: FormFactoryService,
    private householdService: HouseholdService,
    private userService: UserService,
    private metaService: MetaService,
  ) {}

  ngOnInit(): void {
    this.loadInitialData();
  }

  private loadInitialData(): void {
    this.isLoading = true;
    forkJoin({
      members: this.householdmemberService.getAll(),
      meta: this.metaService.getMeta('household-member'),
      households: this.householdService.getAll(),
      users: this.userService.getUsers(),
    }).subscribe({
      next: ({ members, meta, households, users }) => {
        this.houseHoldsMembers = members.response;

        this.householdsMap = Object.fromEntries(
          households.response.map((h: Household) => [h.id, h.name])
        );
        this.usersMap = Object.fromEntries(
          users.response.map((u: User) => [u.id, `${u.name} ${u.surname1} ${u.surname2}`])
        );

        const relationOptions = {
          household: households.response.map((h: Household) => ({ value: h.id as number, label: h.name })),
          user: users.response.map((u: User) => ({ value: u.id as number, label: `${u.name} ${u.surname1} ${u.surname2}` })),
        };

        this.formFields = this.formFactory.enrichMetadataFields(meta.fields, relationOptions);
        const baseCols = this.formFactory.getTableColumnsFromMetadata<HouseHoldMember>(this.formFields);
        this.columns = baseCols.map((col) => {
          if (col.key === 'user_id') return { ...col, formatter: (v: number) => this.usersMap[v] ?? String(v) };
          if (col.key === 'household_id') return { ...col, formatter: (v: number) => this.householdsMap[v] ?? String(v) };
          return col;
        });
        this.isLoading = false;
      },
      error: () => {
        this.errorMessage = 'Error loading Household Members';
        this.isLoading = false;
      },
    });
  }

  editHouseHoldMember(householdmember: HouseHoldMember) {
    this.openDialog(householdmember);
  }

  addHouseHoldMember() {
    this.openDialog();
  }

  openDialog(data?: HouseHoldMember): void {
    const dialogRef = this.dialog.open(GenericDialogComponent, {
      data: {
        title: data ? 'Edit Household Member' : 'New Household Member',
        fields: this.formFields,
        initialData: data || {},
      },
    });

    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        result.id ? this.updateHouseHoldMember(result) : this.createHouseHoldMember(result);
      }
    });
  }

  updateHouseHoldMember(householdMember: HouseHoldMember): void {
    this.householdmemberService.update(householdMember.id!, householdMember).subscribe({
      next: (response: ApiResponse<HouseHoldMember>) => {
        const updated = response.response;
        const index = this.houseHoldsMembers.findIndex((h) => h.id === updated.id);
        if (index !== -1) {
          this.houseHoldsMembers[index] = updated;
          this.houseHoldsMembers = [...this.houseHoldsMembers];
        }
        this.toastService.showToast(response, environment.toastType.Success, {});
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.toastService.showToast(err.error as ApiResponse<string>, environment.toastType.Error, {});
      },
    });
  }

  createHouseHoldMember(householdMember: HouseHoldMember): void {
    this.householdmemberService.create(householdMember).subscribe({
      next: (response: ApiResponse<HouseHoldMember>) => {
        this.houseHoldsMembers.push(response.response);
        this.houseHoldsMembers = [...this.houseHoldsMembers];
        this.toastService.showToast(response, environment.toastType.Success, {});
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.toastService.showToast(err.error as ApiResponse<string>, environment.toastType.Error, {});
      },
    });
  }
}
