
import { CommonModule } from '@angular/common';
import { Component, HostListener, inject } from '@angular/core';
import { DeleteConversationConfirmService } from './delete-conversation-confirm.service';


@Component({
  selector: 'app-delete-conversation-confirm-modal',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './delete-conversation-confirm-modal.component.html',
  styleUrl: './delete-conversation-confirm-modal.component.scss',
})
export class DeleteConversationConfirmModalComponent {
  readonly confirm = inject(DeleteConversationConfirmService);

  close(): void {
    this.confirm.close();
  }

  confirmDelete(): void {
    this.confirm.confirmDelete();
  }

  @HostListener('document:keydown', ['$event'])
  onKeydown(event: Event): void {
    if (!this.confirm.isOpen()) return;

    const keyboardEvent = event as KeyboardEvent;
    if (keyboardEvent.key !== 'Escape') return;

    keyboardEvent.preventDefault();
    this.close();
  }
}
