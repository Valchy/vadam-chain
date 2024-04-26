import { useState, useEffect, useCallback } from 'react';
import { ReloadIcon } from '@radix-ui/react-icons';
import { toast } from 'sonner';
import { Loader2 } from 'lucide-react';

import { Select, SelectContent, SelectGroup, SelectItem, SelectLabel, SelectTrigger, SelectValue } from './components/Select';
import { Table, TableBody, TableCaption, TableCell, TableHead, TableHeader, TableRow } from './components/Table';
import { Input } from './components/Input';
import { Button } from './components/Button';
import { Toaster } from './components/Toast';

function App() {
	const [txBtnDisabled, setTxBtnDisabled] = useState(false);
	const [txAmount, setTxAmount] = useState(undefined);
	const [chosenTxHistoryNode, setChosenTxHistoryNode] = useState(9090);
	const [txHistory, setTxHistory] = useState([]);
	const [senderPeer, setSenderPeer] = useState(undefined);
	const [receiverPeer, setReceiverPeer] = useState(undefined);
	const [key, setKey] = useState(new Date());

	// Request transaction from specific node
	const getTransactions = useCallback((chosenNode, silent) => {
		fetch(`http://localhost:8000/get-transactions/${chosenNode}`, {
			method: 'GET',
			redirect: 'follow',
		})
			.then(response => response.json())
			.then(result => {
				if (!silent) toast.info('Transactions table refreshed!');

				console.log(result);
				setTxHistory(result.transactions);
			})
			.catch(error => {
				if (!silent) toast.error('Some error occurred!');
				console.error(error);
			});
	}, []);

	// On load get transactions
	useEffect(() => getTransactions(9090, true), [getTransactions]);

	// Handle sending transaction
	const handleTransaction = () => {
		if (senderPeer === undefined) return toast.error('Please select a sender peer!');
		if (receiverPeer === undefined) return toast.error('Please select a receiver peer!');
		if (senderPeer % 10 === receiverPeer) return toast.error('Please select different sender and receiver peer!');
		if (!txAmount) return toast.error('Please select amount for transaction!');

		setTxBtnDisabled(true);

		fetch('http://localhost:8000/send-transaction', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({
				node_id: senderPeer,
				peer_id: receiverPeer,
				amount: parseInt(txAmount),
			}),
			redirect: 'follow',
		})
			.then(response => response.json())
			.then(result => console.log(result))
			.catch(error => {
				toast.error('Some error occurred!');
				console.error(error);
			});

		setTimeout(() => {
			getTransactions(chosenTxHistoryNode, true);
			toast.success('Transaction successfully sent!');

			setTxBtnDisabled(false);
			setSenderPeer(undefined);
			setReceiverPeer(undefined);
			setTxAmount('');
			setKey(new Date());
		}, 2500); // so it looks cooler making request seem longer ;)
	};

	return (
		<div className="flex flex-col gap-6 items-center">
			<div className="flex flex-col items-center">
				<b className="mt-10 text-2xl">VADAM-CHAIN</b>
				<p className="text-slate-500 mb-4 text-sm font-light mt-[2px]">When the speed of light is too slow, use vadam-chain.</p>
			</div>
			<div className="flex justify-between items-center w-full max-w-[680px]">
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
					<span className="text-center text-sm mb-1">Amount</span>
					<Input
						value={txAmount}
						disabled={txBtnDisabled}
						onChange={({ target }) => setTxAmount(target.value)}
						placeholder="10 VAD"
						className="w-[80px] text-center"
						max={3}
						onKeyDown={event => {
							const input = event.target;
							const maxDigits = 4;

							if (input.value.length >= maxDigits && !event.metaKey && !event.ctrlKey && event.key !== 'Backspace' && event.key !== 'Delete') {
								event.preventDefault();
							} else if (!/[0-9]/.test(event.key) && event.key !== 'Backspace' && event.key !== 'Delete') {
								// Prevent input if the key pressed is not a number
								event.preventDefault();
							}
						}}
					/>
				</div>
				<span className="mt-7 !font-[monospace]">&gt;&gt;&gt;</span>
				<div className="flex flex-col">
					<span className="text-center text-sm mb-1">Receiver</span>
					<Select disabled={txBtnDisabled} key={key} value={receiverPeer} onValueChange={val => setReceiverPeer(val)}>
						<SelectTrigger className="w-[200px]">
							<SelectValue placeholder="Select a peer..." />
						</SelectTrigger>
						<SelectContent>
							<SelectGroup>
								<SelectLabel>Receiver</SelectLabel>
								<SelectItem value={0}>Peer 1</SelectItem>
								<SelectItem value={1}>Peer 2</SelectItem>
								<SelectItem value={2}>Peer 3</SelectItem>
							</SelectGroup>
						</SelectContent>
					</Select>
				</div>
			</div>
			<Button onClick={handleTransaction} disabled={txBtnDisabled} className="mt-4 w-[160px]">
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
							<TableHead className="w-[980px]">
								<div className="flex justify-between">
									<span>Hash</span>
									<div className="flex justify-between text-center">
										<span className="w-[100px]">Status</span>
										<span className="w-[100px]">Amount</span>
										<span className="w-[100px]">Sender</span>
										<span className="w-[100px]">Receiver</span>
									</div>
								</div>
							</TableHead>
						</TableRow>
					</TableHeader>
					<TableBody>
						{txHistory.map(({ hash_id, status, amount, sender, receiver }) => (
							<TableRow key={hash_id}>
								<TableCell className="font-medium">
									<div className="flex justify-between text-xs">
										<span className="text-slate-400">{hash_id}</span>
										<div className="flex justify-between text-center">
											<span className="w-[100px]">{status}</span>
											<span className="w-[100px]">{amount} VAD</span>
											<span className="w-[100px]">Peer {sender + 1}</span>
											<span className="w-[100px]">Peer {receiver + 1}</span>
										</div>
									</div>
								</TableCell>
							</TableRow>
						))}
					</TableBody>
					<TableCaption>List of selected node's transactions - {txHistory.length}</TableCaption>
				</Table>
			</div>
			<Toaster />
		</div>
	);
}

export default App;
