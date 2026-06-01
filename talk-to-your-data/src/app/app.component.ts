
import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { DeleteConversationConfirmModalComponent } from './shared/delete-conversation-confirm-modal.component';


@Component({
  selector: 'app-root',
  imports: [RouterOutlet, DeleteConversationConfirmModalComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss',
})
export class AppComponent {
  title = 'talk-to-your-data';
}
