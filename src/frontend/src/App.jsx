import { useState } from 'react';
import { ReloadIcon } from '@radix-ui/react-icons';
import { toast } from 'sonner';
import { Loader2 } from 'lucide-react';

import { Select, SelectContent, SelectGroup, SelectItem, SelectLabel, SelectTrigger, SelectValue } from './components/Select';
import { Table, TableBody, TableCaption, TableCell, TableHead, TableHeader, TableRow } from './components/Table';
import { Button } from './components/Button';
import { Toaster } from './components/Toast';

function App() {
	const [txBtnDisabled, setTxBtnDisabled] = useState(false);
	const [chosenTxHistoryNode, setChosenTxHistoryNode] = useState(9090);
	const [txHistory, setTxHistory] = useState(0);
	const [senderPeer, setSenderPeer] = useState(undefined);
	const [recipientPeer, setRecipientPeer] = useState(undefined);
	const [key, setKey] = useState(new Date());

	// Request transaction from specific node
	const getTransactions = chosenNode => {
		fetch(`http://localhost:8000/get-transactions/${chosenNode}`, {
			method: 'GET',
			redirect: 'follow',
		})
			.then(response => response.json())
			.then(result => {
				console.log(result);
				toast('Transactions table refreshed!');
				setTxHistory(result.transactions_made);
			})
			.catch(error => {
				toast('Some error occurred!');
				console.error(error);
			});
	};

	// Handle sending transaction
	const handleTransaction = () => {
		if (senderPeer === undefined) return toast('Please select a sender peer!');
		if (recipientPeer === undefined) return toast('Please select a recipient peer!');
		if (senderPeer % 10 === recipientPeer) return toast('Please select different sender and recipient peer!');

		setTxBtnDisabled(true);

		fetch('http://localhost:8000/send-transaction', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({
				node_id: senderPeer,
				peer_id: recipientPeer,
			}),
			redirect: 'follow',
		})
			.then(response => response.json())
			.then(result => console.log(result))
			.catch(error => {
				toast('Some error occurred!');
				console.error(error);
			});

		setTimeout(() => {
			toast('Transaction successfully sent!');
			setTxBtnDisabled(false);
			setSenderPeer(undefined);
			setRecipientPeer(undefined);
			setKey(new Date());
		}, 2500); // so it looks cooler making request seem longer ;)
	};

	return (
		<div className="flex flex-col gap-6 items-center">
			<div className="flex flex-col items-center">
				<b className="mt-10 text-2xl">VADAM-CHAIN</b>
				<p className="text-slate-500 mb-4 text-sm font-light mt-[2px]">When the speed of light is too slow, use vadam-chain.</p>
			</div>
			<div className="flex justify-between items-center w-full max-w-[480px]">
				<div className="flex flex-col">
					<span className="text-center text-sm mb-1">Sender</span>
					<Select disabled={txBtnDisabled} key={key} value={senderPeer} onValueChange={val => setSenderPeer(val)}>
						<SelectTrigger className="w-[200px]">
							<SelectValue placeholder="Select a peer..." />
						</SelectTrigger>
						<SelectContent>
							<SelectGroup>
								<SelectLabel>Sender</SelectLabel>
								<SelectItem value={9090}>Peer 1</SelectItem>
								<SelectItem value={9091}>Peer 2</SelectItem>
								<SelectItem value={9092}>Peer 3</SelectItem>
							</SelectGroup>
						</SelectContent>
					</Select>
				</div>
				<span className="mt-7 !font-[monospace]">&gt;&gt;&gt;</span>
				<div className="flex flex-col">
					<span className="text-center text-sm mb-1">Recipient</span>
					<Select disabled={txBtnDisabled} key={key} value={recipientPeer} onValueChange={val => setRecipientPeer(val)}>
						<SelectTrigger className="w-[200px]">
							<SelectValue placeholder="Select a peer..." />
						</SelectTrigger>
						<SelectContent>
							<SelectGroup>
								<SelectLabel>Recipient</SelectLabel>
								<SelectItem value={0}>Peer 1</SelectItem>
								<SelectItem value={1}>Peer 2</SelectItem>
								<SelectItem value={2}>Peer 3</SelectItem>
							</SelectGroup>
						</SelectContent>
					</Select>
				</div>
			</div>
			<Button onClick={handleTransaction} disabled={txBtnDisabled} className="mt-2 w-[160px]">
				{txBtnDisabled && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
				{txBtnDisabled ? 'Processing...' : 'Send Transaction'}
			</Button>
			<div className="mt-2">
				<div className="flex justify-between items-center mb-5">
					<h2 className="text-center font-light text-md">Transactions History</h2>
					<div className="flex items-center gap-5">
						<Select
							value={chosenTxHistoryNode}
							onValueChange={val => {
								setChosenTxHistoryNode(val);
								getTransactions(val);
							}}
						>
							<SelectTrigger className="w-[140px]">
								<SelectValue placeholder="Choose node..." />
							</SelectTrigger>
							<SelectContent>
								<SelectGroup>
									<SelectLabel>Fetch data from</SelectLabel>
									<SelectItem value={9090}>Node 1</SelectItem>
									<SelectItem value={9091}>Node 2</SelectItem>
									<SelectItem value={9092}>Node 3</SelectItem>
								</SelectGroup>
							</SelectContent>
						</Select>
						<ReloadIcon onClick={() => getTransactions(chosenTxHistoryNode)} className="cursor-pointer" />
					</div>
				</div>
				<Table>
					<TableHeader>
						<TableRow>
							<TableHead className="w-[680px]">
								<div className="flex justify-between">
									<span>ID</span>
									<div className="flex justify-between w-[200px]">
										<span>Status</span>
										<span className="text-right">Amount</span>
									</div>
								</div>
							</TableHead>
						</TableRow>
					</TableHeader>
					<TableBody>
						{[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18].map(i => (
							<TableRow key={i}>
								<TableCell className="font-medium">
									<div className="flex justify-between">
										<span>TX-000000{i}</span>
										<div className="flex justify-between w-[200px]">
											<span>Processed</span>
											<span className="text-right">{(Math.random() * (4 - 0.2) + 0.2).toFixed(2)} VAD</span>
										</div>
									</div>
								</TableCell>
							</TableRow>
						))}
					</TableBody>
					<TableCaption>List of all processed transactions ({txHistory})</TableCaption>
				</Table>
			</div>
			<Toaster />
		</div>
	);
}

export default App;
