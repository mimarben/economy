import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { GenericDialogComponent } from '../../../shared/generic-dialog/generic-dialog.component';
import { HouseholdMemberBase as HouseHoldMember } from '../../../../models/HouseholdMemberBase';
import { UserBase as User } from '../../../../models/UserBase';
import { HouseholdBase as Household } from '../../../../models/HouseholdBase';
import { GenericTableComponent, TableColumn } from '../../../shared/generic-table/generic-table.component';
import { ApiResponse } from '../../../../models/apiResponse';
import { FormFactoryService } from '../../../../factories/forms/form-factory.service';
import { FormFieldConfig } from '../../../shared/generic-form/form-config';
import { ToastService } from '../../../../services/toast.service';
import { environment } from '../../../../../environments/environment';
import { HouseholdMemberService } from '../../../../services/household-member.service';
import { UserService } from '../../../../services/user.service';
import { HouseholdService } from '../../../../services/household.service';

@Component({
  selector: 'app-householdmembers',
  imports: [GenericTableComponent],
  templateUrl: './householdmembers.component.html',
  styleUrl: './householdmembers.component.css',
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
    private userService: UserService
  ) {}
  ngOnInit(): void {
    this.formFields = this.formFactory.getFormConfig('houseHoldMember');
    this.columns =this.formFactory.getTableColumns<HouseHoldMember>(
                                                                    'houseHoldMember',
                                                                    {user_id:  (value: number) => this.usersMap[value] ?? value, household_id: (value: number) => this.householdsMap[value] ?? value });
    this.loadHouseHoldMembers();
    this.loadUsers();
    this.loadHouseHold();
  }
  loadHouseHoldMembers() {
    this.isLoading = true;
    this.householdmemberService.getAll().subscribe({
      next: (data: ApiResponse<HouseHoldMember[]>) => {
        this.houseHoldsMembers = data.response;
        this.isLoading = false;
      },
      error: (err) => {
        this.errorMessage = 'Error loading banks';
        this.isLoading = false;
      },
    });

    this.householdService.getAll().subscribe({
      next: (res: ApiResponse<Household[]>) => {
        const householdField = this.formFields.find(f => f.key === 'household_id');
        if (householdField) {
          this.householdsMap = Object.fromEntries(res.response.map(h=>[h.id,h.name]));
        }
      }
    });
    this.userService.getUsers().subscribe({
      next: (res: ApiResponse<User[]>) => {
        const userField = this.formFields.find(f => f.key === 'user_id');
        if (userField) {
          this.usersMap = Object.fromEntries(res.response.map(u=>[u.id, (`${u.name} ${u.surname1} ${u.surname2}`)]))
        }
      }
    });
  }
  private loadUsers(): void {
    this.userService.getUsers().subscribe({
      next: (res: ApiResponse<User[]>) => {
        const field = this.formFields.find(f => f.key === 'user_id');
        if (field) {
          field.type = 'select';
          field.options = res.response.map(u => ({ label: `${u.name} ${u.surname1} ${u.surname2}`, value: u.id }));
        }
      },
      error: () => {
        this.errorMessage = 'Error loading users';
        this.isLoading = false;
      }
    });
  }
  private loadHouseHold(): void {
    this.householdService.getAll().subscribe({
      next: (res: ApiResponse<Household[]>) => {
        const field = this.formFields.find(f => f.key === 'household_id');
        if (field) {
          field.type = 'select';
          field.options = res.response.map(u => ({ label: `${u.name}`, value: u.id }));
        }
      },
      error: () => {
        this.errorMessage = 'Error loading users';
        this.isLoading = false;
      }
    });
  }
  editHouseHoldMember(householdmember: HouseHoldMember) {
    this.openDialog(householdmember);

  }
  addHouseHoldMember() {
    this.openDialog();
  }

  openDialog(data?: HouseHoldMember): void{
    const diaglogRef = this.dialog.open(GenericDialogComponent,{
      data: {
        title: data? 'Edit HouseHold Member' : 'New HoseHold Memeber',
        fields: this.formFactory.getFormConfig('houseHoldMember'),
        initialData: data || {},
      }
    });
    diaglogRef.afterClosed().subscribe((result)=>{
      if(result){
        result.id ? this.updateHouseHoldMember(result): this.createHouseHoldMember(result);
      }
    });
  }
  updateHouseHoldMember(householdMember: HouseHoldMember): void {
    this.householdmemberService.update(householdMember.id, householdMember).subscribe({
    next: (response: ApiResponse<HouseHoldMember>) => {
      const updated = response.response;
      const index = this.houseHoldsMembers.findIndex(h => h.id === updated.id);
      if (index !== -1) {
        this.houseHoldsMembers[index] = updated;
        this.houseHoldsMembers = [...this.houseHoldsMembers];
      }
      this.toastService.showToast(response, environment.toastType.Success, {});
      this.cdr.detectChanges();
    },
    error: (err) => {
      this.toastService.showToast(err.error as ApiResponse<string>, environment.toastType.Error, {});
    }
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
    }
  });
  }
}
