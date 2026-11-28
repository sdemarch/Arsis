import { Directive, ElementRef, HostListener, inject } from '@angular/core';

/**
 * Opens the browser's own calendar (or time) picker when the field is clicked,
 * instead of leaving the user to type into the date segments.
 */
@Directive({ selector: 'input[arsisOpenPicker]' })
export class OpenPickerDirective {
  private readonly input = inject<ElementRef<HTMLInputElement>>(ElementRef).nativeElement;

  @HostListener('click')
  open(): void {
    try {
      this.input.showPicker?.();
    } catch {
      // Not allowed (e.g. a disabled field) or unsupported: typing still works.
    }
  }
}
